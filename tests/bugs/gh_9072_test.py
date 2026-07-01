#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9072
TITLE:       gbak restore fails with "Implementation of text subtype 52 not located" after restoring a WIN1251 user collation
DESCRIPTION:
    We use initial script from the ticket and try to do bacup-restore via two ways:
    * using 'gbak -b' / 'gbak -rep' and remote protocol;
    * using services API and ability to run local_backup / local_restore.
    Both ways must pass.
    Finally, we compare content of firebird.log before and after these tests -- no difference must appear.
NOTES:
    [01.07.2026] pzotov
    Confirmed problems on 6.0.0.2028-348f7aa:
        * restore using gbak failed with 'gbak: ERROR: "PUBLIC"."SYS_DOMAINS" / Implementation of text subtype 52 not located'
        * usage of srv.database.local_restore failed with 'Error writing data to the connection', firebird.log after this had:
          'internal Firebird consistency check (pointer page lost from DPM_delete_relation (246), file: dpm.cpp line: 1379)'
    Checked on 6.0.0.2050-09246e5.
"""
from io import BytesIO
from pathlib import Path
from difflib import unified_diff
import locale
from firebird.driver import SrvRestoreFlag, DatabaseError

import pytest
from firebird.qa import *

init_script = """
    set bail on;
    create collation rdb_win1251_repro
      for system.win1251
      from external ('WIN1251_UNICODE');

    create domain d_win1251_repro
      as varchar(31) character set system.win1251;

    create table sys_domains (
        id integer not null,
        name d_win1251_repro,
        val varchar(31) character set system.win1251
    );

    insert into sys_domains(id, name, val) values (1, 'оперный', 'театр');
    commit;
"""

db = db_factory(init = init_script, charset = 'utf8')
tmp_res_fdb = db_factory(filename = 'tmp_9072_res.fdb')

act = python_act('db', substitutions=[('[ \t]+', ' ')])
act_res_fdb = python_act('tmp_res_fdb')

tmp_fbk = temp_file('tmp_9072.fbk')
tmp_res = temp_file('tmp_9072_restored.fdb')

@pytest.mark.version('>=6.0')
def test_1(act: Action, act_res_fdb: Action, tmp_fbk: Path, capsys):

    # Get FB log before test:
    fblog_1 = act.get_firebird_log()

    # ........................................................................
    # test N 1:
    try:
        act.gbak(switches = ['-b', act.db.dsn, str(tmp_fbk)], io_enc = locale.getpreferredencoding())
        act.gbak(switches = ['-rep', '-v', str(tmp_fbk), act_res_fdb.db.dsn ], io_enc = locale.getpreferredencoding())
    except ExecutionError as e:
        print('test-1 failed:')
        print('++++++++++++++++++++++++')
        print(e)
        print('++++++++++++++++++++++++')
        print(act.clean_stderr)

    act_res_fdb.db.db_path.unlink(missing_ok = True)

    # ........................................................................
    # test N 2:
    backup = BytesIO()
    try:
        with act.connect_server() as srv: # <<< FB crashed before fix at this point.
            srv.database.local_backup(database = act.db.db_path, backup_stream = backup)
            backup.seek(0)
            srv.database.local_restore(backup_stream = backup, database = act_res_fdb.db.db_path, flags = SrvRestoreFlag.REPLACE)
    except DatabaseError as e:
        print('test-2 failed:')
        print('++++++++++++++++++++++++')
        print(e)
        print('++++++++++++++++++++++++')

    # ........................................................................

    # Obtain firebird.log after test. No difference must exists:
    fblog_2 = act.get_firebird_log()

    for i, line in enumerate(unified_diff(fblog_1, fblog_2)):
        if i == 0:
            print('UNEXPECTED line(s) in firebird.log:')
        if line.startswith('+') and line[1:].strip():
            print(line)

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == ''
