#coding:utf-8

"""
ID:          issue-6492
ISSUE:       6492
TITLE:       A number of errors when database name is longer than 255 symbols
DESCRIPTION:
  Test verifies that one may to create DB with total path plus name length L = 255 and 259 characters.
  Each DB is then subject for 'gbak -b', 'gbak -c', 'gstat -h', 'gfix -sweep' and 'gfix -v -full'.
  All these commands must NOT issue something to their STDERR.

  STDOUT-log of initial SQL must contain full DB name.
  Changed part of firebird.log for SWEEP and VALIDATION also must have full DB name (this is verified using regexp):
  +[tab]Database: C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\ABC.FDB // for validation
  +[tab]Database "C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\ABC.FDB // for sweep

  STDOUT-logs of backup, restore and gstat currently (09-mar-2020) have only truncated name (~235...241 chars).
  This may change in the future if FB developers will decide to fix this small inconveniences.

  For L=259 we must see in backup log following phrase:
    gbak:text for attribute 7 is too large in put_asciz(), truncating to 255 bytes
  - but currently this is not checked here.
[09.02.2022] pcisar
  Fails on Windows10 / 4.0.1 with:
   "CreateFile (create)" operation for file "..."
    -Error while trying to create file
    -System can't find specified path
  Variant with 255 chars fails in init script, while 259 chars variant fails in database fixture while
  db creation.
  On national windows with OS i/o error messages in locale.getpreferredencoding(), it may fail while
  reading stderr from isql. But using io_enc=locale.getpreferredencoding() will show the message.
JIRA:        CORE-6248
FBTEST:      bugs.core_6248
"""

import pytest
import re
import time
import platform
from difflib import unified_diff
from firebird.qa import *
from firebird.driver import SrvRepairFlag

init_script = """
    set list on;

    create exception exc_dbname_diff q'{Value in mon$database.mon$database_name differs from rdb$get_context('SYSTEM', 'DB_NAME'):@1@2@3=== vs ===@4@5}';
    set term ^;
    execute block returns(
         mon_database_column varchar(260)
        ,sys_context_db_name varchar(260)
    ) as
        declare lf char(1) = x'0A';
    begin
        select
            mon$database_name as mon_database_column
        from mon$database
        into mon_database_column;

        sys_context_db_name = rdb$get_context('SYSTEM', 'DB_NAME');

        if ( substring( sys_context_db_name from 1 for 255 ) is distinct from mon_database_column ) then
        begin
            exception exc_dbname_diff using(
                lf
                ,mon_database_column
                ,lf
                ,lf
                ,sys_context_db_name
            );
        end

        suspend;
    end
    ^
    set term ;^
    commit;
"""

db = db_factory()

act = python_act('db')

expected_stdout = """
    ddl : found at least 255 characters
    backup : found truncated DB name.
    restore : found truncated DB name.
    gstat : found truncated DB name.
    fblog_diff_sweep : found at least 255 characters
    fblog_diff_validate : found at least 255 characters
"""

@pytest.fixture
def test_db(request: pytest.FixtureRequest, db_path) -> Database:
    required_name_len = request.param[0]
    chars2fil = request.param[1]
    filename = (chars2fil * 1000)[:required_name_len - len(str(db_path)) - 4] + '.fdb'
    db = Database(db_path, filename)
    db.create()
    yield db
    db.drop()

MINIMAL_LEN_TO_SHOW = 255

PATTERN = re.compile('\\+\\s+Database[:]{0,1}\\s+"{0,1}', re.IGNORECASE)

def check_filename_presence(lines, *, log_name: str, db: Database):
    filename = str(db.db_path) # To convert Path to string
    for line in lines:
        if log_name not in ('fblog_diff_sweep', 'fblog_diff_validate') or line.startswith('+') and PATTERN.search(line):
            if filename[:MINIMAL_LEN_TO_SHOW].upper() in line.upper():
                print(f'{log_name} : found at least {str(MINIMAL_LEN_TO_SHOW)} characters')
                return
            elif filename[:128].upper() in line.upper():
                print(f'{log_name} : found truncated DB name.')
                return
    print(f'{log_name} : DB NAME NOT FOUND')


@pytest.mark.skipif(platform.system() == 'Windows', reason='FIXME: see notes')
@pytest.mark.version('>=4.0')
@pytest.mark.parametrize('test_db', [pytest.param((255, 'abc255def'), id='255'),
                                     pytest.param((259, 'qwe259rty'), id='259')], indirect=True)
def test_1(act: Action, test_db: Database, capsys):
    # INIT test
    act.isql(switches=['-q', test_db.dsn], input=init_script, connect_db=False)
    check_filename_presence(act.stdout.splitlines(), log_name='ddl', db=test_db)
    # GBAK BACKUP test
    backup_name = test_db.db_path.with_name(f"tmp_6248_backup_{len(test_db.db_path.with_suffix('').name)}.fbk")
    act.reset()
    act.gbak(switches=['-b', '-se', 'localhost:servce_mgr', '-v', '-st', 'tdwr', str(test_db.db_path), str(backup_name)])
    check_filename_presence(act.stdout.splitlines(), log_name='backup', db=test_db)
    # GBAK RESTORE test
    act.reset()
    act.gbak(switches=['-rep', '-se', 'localhost:servce_mgr', '-v', '-st', 'tdwr', str(backup_name), str(test_db.db_path)])
    check_filename_presence(act.stdout.splitlines(), log_name='restore', db=test_db)
    # GSTAT test
    act.reset()
    act.gstat(switches=['-h', test_db.dsn], connect_db=False)
    check_filename_presence(act.stdout.splitlines(), log_name='gstat', db=test_db)
    # SWEEP test
    log_before = act.get_firebird_log()
    with act.connect_server() as srv:
        srv.database.sweep(database=test_db.db_path)
    time.sleep(1) # Let firebird.log to be fulfilled with text about just finished SWEEP
    log_after = act.get_firebird_log()
    check_filename_presence(list(unified_diff(log_before, log_after)), log_name='fblog_diff_sweep', db=test_db)
    # VALIDATE test
    log_before = act.get_firebird_log()
    with act.connect_server() as srv:
        srv.database.repair(database=test_db.db_path, flags=SrvRepairFlag.FULL | SrvRepairFlag.VALIDATE_DB)
    time.sleep(1) # Let firebird.log to be fulfilled with text about just finished VALIDATION
    log_after = act.get_firebird_log()
    check_filename_presence(list(unified_diff(log_before, log_after)), log_name='fblog_diff_validate', db=test_db)
    # Check
    act.reset()
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
