#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9083
TITLE:       Firebird 6.0.0 can't restore local SP referencing system table
DESCRIPTION:
    Test uses backup of database that was created in ODS 13.1 (FB 5.0.5.1861).
    It contains standalone procedure, function and package that has similar proc and func:
    every such unit has inner sub-routine which is called.

    We extract this .fbk from .zip and try to restore from it using services API. No errors must occur.
    Finally, we run query to DB procedure, function and package units. It must run w/o errors.
NOTES:
    [13.07.2026] pzotov
    Confirmed bug on 6.0.0.2072-42c8a5d, got on restore:
        table "PUBLIC"."RDB$RELATION_FIELDS" is not defined
        -Exiting before completion due to errors
        (335544395, 336330835)
    Checked on 6.0.0.2073-3518df8.
"""

import pytest
import zipfile
import locale
from pathlib import Path
from firebird.qa import *
from firebird.driver import SrvRestoreFlag, DatabaseError

db = db_factory()

act = python_act('db', substitutions=[('[ \t]+', ' ')])

tmp_fbk = temp_file('gh_9083-ods13_1.fbk')
tmp_fdb = temp_file('tmp_restore_9083.fdb')

#------------------------------------------------------------------
# Callback function: capture output of ERROR messages in restore (output must be empty):
def print_log(line: str) -> None:
    if ( s:= line.strip()):
        if 'ERROR' in s:
            print(s)
#------------------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_fbk: Path, tmp_fdb: Path, capsys):

    zipped_fbk_file = zipfile.Path(act.files_dir / 'gh_9083-ods13_1.zip', at = 'gh_9083-ods13_1.fbk')
    tmp_fbk.write_bytes(zipped_fbk_file.read_bytes())
    #
    restore_log = []
    test_sql = """
        set list on;
        select p.result as standalone_sp_result from sp_read_systable_from_local_sp p;
        select fn_read_systable_from_local_fn() standalone_fn_result from rdb$database;
        select p.result as packaged_sp_result from pg_read_systable_from_local_units.sp_read_systable_from_local_sp p;
        select pg_read_systable_from_local_units.fn_read_systable_from_local_fn() as packaged_fn_result from rdb$database;
    """
    with act.connect_server(encoding_errors = locale.getpreferredencoding()) as srv:
        try:
            srv.database.restore(backup=tmp_fbk, database=tmp_fdb, flags=SrvRestoreFlag.REPLACE, verbose=True, callback = print_log)
            act.isql( switches=[ str(tmp_fdb), '-q' ], connect_db = False, input = test_sql, combine_output = True )
            print(act.stdout)
        except DatabaseError as e:
            print(f'Restore failed:')
            print(e.__str__())
            print(e.gds_codes)
        except Exception as x:
            print(x)

    act.expected_stdout = """
        STANDALONE_SP_RESULT 1
        STANDALONE_FN_RESULT 1
        PACKAGED_SP_RESULT 2
        PACKAGED_FN_RESULT 2
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
