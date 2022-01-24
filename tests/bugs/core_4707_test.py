#coding:utf-8

"""
ID:          issue-5015
ISSUE:       5015
TITLE:       Implement ability to validate tables and indices online (without exclusive access to database)
DESCRIPTION:
JIRA:        CORE-4707
"""

import pytest
import subprocess
import time
from pathlib import Path
from firebird.qa import *

init_script = """
    set term ^;
    execute block as
    begin
        execute statement 'drop sequence g';
    when any do begin end
    end^
    set term ;^
    commit;
    create sequence g;
    commit;
    recreate table test1(id int, s varchar(1000));
    recreate table test2(id int primary key using index test2_pk, s varchar(1000), t computed by (s) );
    recreate table test3(id int);
    commit;

    insert into test1(id, s) select gen_id(g,1), rpad('', 1000, gen_id(g,0) ) from rdb$types rows 100;
    insert into test2(id, s) select id, s from test1;
    commit;

    create index test2_s on test2(s);
    create index test2_c on test2 computed by(s);
    create index test2_t on test2 computed by(t);
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db', substitutions=[('[\\d]{2}:[\\d]{2}:[\\d]{2}.[\\d]{2}', ''),
                                      ('Relation [\\d]{3,4}', 'Relation')])

expected_stdout = """
    ISQL_MSG                        Starting EB with infinite pause.
    08:37:01.14 Validation started
    08:37:01.15 Relation 128 (TEST1)
    08:37:02.15 Acquire relation lock failed
    08:37:02.15 Relation 128 (TEST1) : 1 ERRORS found
    08:37:02.15 Relation 129 (TEST2)
    08:37:02.15   process pointer page    0 of    1
    08:37:02.15 Index 1 (TEST2_PK)
    08:37:02.15 Index 2 (TEST2_S)
    08:37:02.15 Index 3 (TEST2_C)
    08:37:02.15 Index 4 (TEST2_T)
    08:37:02.17 Relation 129 (TEST2) is ok
    08:37:02.17 Relation 130 (TEST3)
    08:37:03.17 Acquire relation lock failed
    08:37:03.17 Relation 130 (TEST3) : 1 ERRORS found
    08:37:03.17 Validation finished
"""

hang_script_file = temp_file('hang_script.sql')
hang_output = temp_file('hang_script.out')

@pytest.mark.version('>=2.5.5')
def test_1(act: Action, hang_script_file: Path, hang_output: Path, capsys, request):
    # Fializer for FB4
    def drop_connections():
        with act.db.connect() as con4cleanup:
            con4cleanup.execute_immediate('delete from mon$attachments where mon$attachment_id != current_connection')
            con4cleanup.commit()

    request.addfinalizer(drop_connections)
    # Following script will hang for sevral seconds (see 'lock timeout' argument - and this will serve as pause
    # during which we can launch fbsvcmgr to validate database:
    hang_script_file.write_text(f"""
    set term ^;
    execute block as
    begin
      execute statement 'drop role tmp$r4707';
      when any do begin end
    end ^
    set term ;^
    commit;

    set transaction wait;

    delete from test1;
    insert into test3(id) values(1);
    set list on;
    select 'Starting EB with infinite pause.' as isql_msg from rdb$database;
    set term ^;
    execute block as
    begin
      execute statement 'update test1 set id=-id'
      on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
      as user '{act.db.user}' password '{act.db.password}'
         role 'TMP$R4707' -- this will force to create new attachment, and its Tx will be paused on INFINITE time.
      ;
      when any do begin end
    end ^
    set term ;^
    select 'EB with pause finished.' as msg_2 from rdb$database;
    """)
    # Make asynchronous call of ISQL which will stay several seconds in pause due to row-level lock
    with open(hang_output, mode='w') as hang_out:
        p_hang_sql = subprocess.Popen([act.vars['isql'], '-i', str(hang_script_file),
                                       '-user', act.db.user,
                                       '-password', act.db.password, act.db.dsn],
                                       stdout=hang_out, stderr=subprocess.STDOUT)
        try:
            time.sleep(2)
            # Make SYNC. call of fbsvcmgr in order to validate database which has locks on some relations
            act.svcmgr(switches=['action_validate', 'dbname', str(act.db.db_path),
                                   'val_lock_timeout', '1'])
        finally:
            p_hang_sql.terminate()
    #
    print(hang_output.read_text())
    print(act.stdout)
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
