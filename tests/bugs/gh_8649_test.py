#coding:utf-8

"""
ID:          n/a
ISSUE:       8649
TITLE:       AV when ON CONNECT triggers uses EXECUTE STATEMENT ON EXTERNAL
DESCRIPTION:
NOTES:
    [13.07.2025] pzotov
    1. On localized Windows non-ascii message appears in output:
         335544734 : Error while trying to open file
         85767113 : <file not found> // localized message here
         Data source : Firebird::localhost:
       We have to filter out all such messages, see substitutions.
    2. By default, any test database is created with flag 'do_not_drop = False' which means that such DB
       will be dropped at teardown phase of pytest.
       Appropriate method of Database class does following:
           1.   Changes test DB linger to 0 (using services API);
           2.   Establishes new common connection (i.e. no_db_triggers = False) which:
           2.1.   Issues 'delete from mon$attachments', with suppressing any exceptions
           2.2.   Calls drop_database(), also with suppressing any exceptions
           3.   If DB file still exists - calls self.db_path.unlink(missing_ok=True)
       This means that on step "2." DB-level triggers will fire, even if they are invalid or cause problems.
       We *ourselves* have to drop such triggers, BEFORE teardown - see 'con_kill_db_level_trigger'.
    3. Name of trigger must be adjusted on FB 6.x because of SQL schemas introduction since 6.0.0.834

    Confirmed bug (crash) on 6.0.0.949; 5.0.3.1668; 4.0.6.3214.
    Checked on 6.0.0.967; 5.0.3.1683; 4.0.6.3221
"""
import locale
from pathlib import Path
import pytest
from firebird.qa import *

db = db_factory()
tmp_fdb = temp_file('tmp_gh_8649.fdb')

substitutions = [  ('^((?!(SQLSTATE|error|Error|TRG_CONNECT|source)).)*$', '')
                  ,('operation for file .*', 'operation for file')
                  ,('Data source : Firebird::.*', 'Data source : Firebird::')
                  ,(r'line(:)?\s+\d+.*', '')
                ]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=4.0.6')
def test_1(act: Action, tmp_fdb: Path):

    test_script = f"""
        set term ^;
        create trigger trg_connect on connect as
            declare id int;
        begin
            execute statement 'select 1 from rdb$database'
            on external 'localhost:{str(tmp_fdb)}'
        	into :id;
        end
        ^
        set term ;^
        commit;
        connect '{act.db.dsn}';
    """

    TEST_TRIGGER_NAME = "'TRG_CONNECT'" if act.is_version('<6') else '"PUBLIC"."TRG_CONNECT"'
    act.expected_stdout = f"""
        Statement failed, SQLSTATE = 42000
        Execute statement error at attach :
        335544344 : I/O error during "CreateFile (open)" operation for file
        335544734 : Error while trying to open file
        Data source : Firebird::
        -At trigger {TEST_TRIGGER_NAME}
    """

    act.isql(switches=['-q'], charset = 'utf8', input = test_script, combine_output = True, io_enc = locale.getpreferredencoding())
    
    # ::: ACHTUNG :::
    # Special connection must be done here, with ignoring DB-level triggers.
    # We have to drop such trigger otherwise problem will raise at teardown phase!
    #
    with act.db.connect(no_db_triggers = True) as con_kill_db_level_trigger:
        con_kill_db_level_trigger.execute_immediate('drop trigger trg_connect')
        con_kill_db_level_trigger.commit()

    assert act.clean_stdout == act.clean_expected_stdout
