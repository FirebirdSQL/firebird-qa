#coding:utf-8

"""
ID:          issue-4310
ISSUE:       4310
TITLE:       DELETE FROM MON$STATEMENTS does not interrupt a longish fetch
DESCRIPTION:
NOTES:
[02.11.2019]
  restored DB state must be changed to full shutdown in order to make sure tha all attachments are gone.
  Otherwise one may get:
    Error while dropping database
    - SQLCODE: -901
    - lock time-out on wait transaction
    - object E:\\QA\\FBT-REPO\\TMP\\BUGS.CORE_3977.FDB is in use
  This is actual for 4.0+ SS/SC when ExtConnPoolLifeTime > 0.
JIRA:        CORE-3977
FBTEST:      bugs.core_3977
"""

import pytest
import subprocess
import time
from pathlib import Path
from firebird.qa import *

init_script = """
    create sequence g;
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db', substitutions=[('^((?!RECORDS AFFECTED:|RESULT_MSG).)*$', '')])

expected_stdout = """
    DEL FROM MON$STTM:  RECORDS AFFECTED: 2
    CHECK RESULTS LOG:  RESULT_MSG OK: QUERY WAS INTERRUPTED IN THE MIDDLE POINT.
    CHECK RESULTS LOG:  RECORDS AFFECTED: 1
"""

work_script_1 = temp_file('work_script.sql')

@pytest.mark.version('>=3')
def test_1(act: Action, work_script_1: Path, capsys):
    work_script_1.write_text(f"""
    alter sequence g restart with 0;
    commit;

    set term ^;
    execute block as
        declare x int;
    begin
        for
            execute statement ('select gen_id(g,1) from rdb$types,rdb$types,rdb$types')
            on external
                'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
                as user '{act.db.user}' password '{act.db.password}'
            into x
        do begin
        end
    end
    ^
    set term ;^
    """)
    # Starting ISQL in separate process with doing 'heavy query'
    p_work_sql = subprocess.Popen([act.vars['isql'], '-i', str(work_script_1),
                                   '-user', act.db.user,
                                   '-password', act.db.password, act.db.dsn],
                                  stderr = subprocess.STDOUT)
    time.sleep(3)
    # Run 2nd isql and issue there DELETE FROM MON$ATATSMENTS command. First ISQL process should be terminated for short time.
    drop_sql = """
    commit;
    set list on;

    select *
    from mon$statements
    where
        mon$attachment_id != current_connection
        and mon$sql_text containing 'gen_id('
    --order by mon$stat_id
    ;

    set count on;

    delete from mon$statements
    where
        mon$attachment_id != current_connection
        and mon$sql_text containing 'gen_id('
    --order by mon$stat_id
    ;
    quit;
"""
    try:
        act.isql(switches=[], input=drop_sql)
        delete_from_mon_sttm_log = act.string_strip(act.stdout)
    finally:
        p_work_sql.terminate()
    # Run checking query: what is resuling value of sequence 'g' ?
    # (it must be > 0 and < total number of records to be handled).
    check_sql = """
    --set echo on;
    set list on;
    set count on;
    select iif( current_gen > 0 and current_gen < total_rows,
                'OK: query was interrupted in the middle point.',
                'WRONG! Query to be interrupted '
                || iif(current_gen <= 0, 'did not start.', 'already gone, current_gen = '||current_gen )
              ) as result_msg
    from (
        select gen_id(g,0) as current_gen, c.n * c.n * c.n as total_rows
        from (select (select count(*) from rdb$types) as n from rdb$database) c
    );
"""
    act.isql(switches=[], input=check_sql)
    #
    for line in delete_from_mon_sttm_log.splitlines():
        if not 'EXECUTE STATEMENT' in line.upper():
            print('DEL FROM MON$STTM: ', ' '.join(line.upper().split()))
    for line in act.string_strip(act.stdout).splitlines():
        print('CHECK RESULTS LOG: ', ' '.join(line.upper().split()))
    #
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
