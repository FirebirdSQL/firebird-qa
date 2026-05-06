#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/ee28aa6f6c63f4e987471a32d538bf09b5219833
TITLE:       Hang (assert in DEV) with ALTER TABLE tbl ALTER fld TYPE ... when "tbl" has conditional index and condition depends on "fld"
DESCRIPTION:
    The problem has been encountered during re-implementing test for #8950 because of shared metacache: re-connect was required
    after 'ALTER TABLE ... ALTER COOLUMN ...', otherwise FB did hang.
    Trace did show error with messages: 
        335545102 : Error during savepoint backout - transaction invalidated
        335544382 : Statement format outdated, need to be reprepared'
    Key notes:
        * partial index required; regular or computed-by indices does not affect;
        * the altered table must have at least one record before ALTER TABLE is issued.
NOTES:
    [06.05.2026] pzotov
    Test creates temporary .fdb file which will be used as database for checking issue.
    We must avoid to use test DB defined by db_factory() because in this case pytest may hang on teardown phase.
    (console will contain 'FAIL' outcome but control will not return to pytest -- at least on Windows).
    Discussed with Alex, letters since 04.04.2026 1419
    Confirmed bug on 6.0.0.1929-4dd80ed.
    Checked on 6.0.0.1930-ee28aa6.
"""
from pathlib import Path
import subprocess
import tempfile
import random
import string
import time

import pytest
from firebird.qa import *
db = db_factory()
act = python_act('db')

MAX_TIMEOUT = 5
EXPECTED_MSG = 'Completed.'
INDEX_NAME = 'test_partial'

tmp_sql = temp_file('tmp_ee28aa6f.sql')
tmp_log = temp_file('tmp_ee28aa6f.log')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, tmp_log: Path, capsys):

    tmp_fdb = Path(tempfile.gettempdir()) / ( 'test_ee28aa6f.' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + '.fdb')
    test_sql = f"""
        create database 'localhost:{tmp_fdb}' user {act.db.user} password '{act.db.password}';
        set heading off;
        set autoddl off;
        recreate table test(f01 smallint);
        create index {INDEX_NAME} on test(f01) where f01 is not null;
        commit;
        insert into test(f01) values(null);
        commit;
         
        alter table test alter f01 type varchar(20);
        commit;
         
        insert into test(f01) values('{EXPECTED_MSG}');

        set plan on;
        set count on;
        select f01 from test where f01 is not null;
    """

    tmp_sql.write_text(test_sql)

    # If the timeout expires, the child process will be killed and waited for.
    # The TimeoutExpired exception will be re-raised after the child process has terminated.
    tmp_log.unlink(missing_ok = True)
    rc = 0
    try:
        cmd_isql = [act.vars['isql'], '-q', '-i', str(tmp_sql)]
        with open(tmp_log, 'w') as f:
            p = subprocess.run( cmd_isql, stdout = f, stderr = subprocess.STDOUT, timeout = MAX_TIMEOUT)
            rc = p.returncode
    except Exception as e:
        print(f'{e.__class__=}')
        # DO NOT: print(f'{e.errno=}') AttributeError: 'TimeoutExpired' object has no attribute 'errno'
        # Command '[...]'  timed out after NNN seconds
        print(e.__str__())
        rc = -987654321 # need because timeout does not change returncode!
        
    print(f'ISQL returncode: {rc}')

    if rc != 0:
        print('Check script:')
        print(tmp_sql.read_text())

    if tmp_log.is_file():
        print('Check log:')
        with open(tmp_log, 'r') as f:
            for line in f:
                print(line)

    act.expected_stdout = f"""
        ISQL returncode: 0
        Check log:
        PLAN ("PUBLIC"."TEST" INDEX ("PUBLIC"."{INDEX_NAME.upper()}"))
        {EXPECTED_MSG}
        Records affected: 1
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
