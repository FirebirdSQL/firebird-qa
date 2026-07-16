#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9087
TITLE:       Firebird 6.0.0 restore resets changed default database collation of FB5 database to system default
DESCRIPTION:
    Test uses backup of database that was created in ODS 13.1 (FB 5.0.5.1861).
    This DB has the only changed property: charset ISO8859_1 has default collation = DE_DE (it was changed before backup).

    We extract this .fbk from .zip and try to restore from it.
    Running query to RDB$CHARACTER_SETS must show outcome with rdb$default_collate_name = DE_DE.
    Before fix this query issued 'ISO8859_1' in this column instead of 'DE_DE'.
NOTES:
    [16.07.2026] pzotov
    Confirmed bug on 6.0.0.2073-3518df8.
    Checked on 6.0.0.2074-7df850d
"""

import pytest
import zipfile
import locale
from pathlib import Path
from firebird.qa import *
from firebird.driver import SrvRestoreFlag, DatabaseError

db = db_factory()

act = python_act('db', substitutions=[('[ \t]+', ' ')])

tmp_fbk = temp_file('gh_9087-ods13_1.fbk')
tmp_fdb = temp_file('tmp_restore_9087.fdb')

#------------------------------------------------------------------
# Callback function: capture output of ERROR messages in restore (output must be empty):
def print_log(line: str) -> None:
    if ( s:= line.strip()):
        if 'ERROR' in s:
            print(s)
#------------------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_fbk: Path, tmp_fdb: Path, capsys):

    zipped_fbk_file = zipfile.Path(act.files_dir / 'gh_9087-ods13_1.zip', at = 'gh_9087-ods13_1.fbk')
    tmp_fbk.write_bytes(zipped_fbk_file.read_bytes())

    test_sql = """
        set list on;
        select rdb$character_set_name as rdb_cset_name, rdb$default_collate_name as rdb_default_coll
        from rdb$character_sets where
        rdb$character_set_name = upper('ISO8859_1'); 
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
        RDB_CSET_NAME    ISO8859_1
        RDB_DEFAULT_COLL DE_DE
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
