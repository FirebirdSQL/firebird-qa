#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/3904
TITLE:       GFIX returns an error after correctly shutting down a database
DESCRIPTION: Affects only local connections
JIRA:        CORE-3548
NOTES:
    [19.07.2026] pzotov
    ::: NOTE for 6.x :::
    since https://github.com/FirebirdSQL/firebird/commit/afb9dc806cb3fe23685f3bfafd1dd91d866a453f it is unable to get DB header via TCP:
    permissions are validated for remote protocol remotely and this is done before the header is printed. But it's impossible to attach
    the database in the full shutdown mode.
    Explained by dimitr: https://groups.google.com/g/firebird-devel/c/PP7rxLrdsLE/m/hnbPDqHCBQAJ
    This means that either fbsvcmgr or gstat will fail if DB name is prefixed by 'localhost:' or 'inet://'.
    Because of this, invocation of srv.database.get_statistics() was replaced with trivial 'gstat -h': we have to check in this test
    only presense of 'Attributes full shutdown' line in the DB header after 'gfix -shut' command completes.

    Checked on 6.0.0.2079; 5.0.5.1861; 4.0.8.3286; 3.0.15.33867   
"""
import locale
import pytest
from firebird.qa import *
from firebird.driver import SrvStatFlag, DatabaseError

db = db_factory()

substitutions = [ ('^((?!Attribute|connection).)*$', ''), ('[ \t]+', ' ') ]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=3')
def test_1(act: Action, capsys):
    act.gfix( switches = ['-user', act.db.user, '-password', act.db.password, '-shut', 'full', '-force', '0', str(act.db.db_path) ], io_enc = locale.getpreferredencoding(), combine_output = True )
    assert act.return_code == 0 and act.stdout == '' , f'Could not change DB state to full shutdown:\n{act.clean_stdout}'
    act.reset()
    
    hdr_info = ''
    try:
        act.gstat( switches = ['-h', str(act.db.db_path)], connect_db=False  ) 
        hdr_info = act.clean_stdout
        act.reset()
        act.gfix( switches = ['-user', act.db.user, '-password', act.db.password, '-online', str(act.db.db_path) ], io_enc = locale.getpreferredencoding(), combine_output = True )
        assert act.return_code == 0 and act.stdout == '' , f'Could not return DB to online state:\n{act.clean_stdout}'
    except DatabaseError as e:
        print(e.__str__())
        for x in e.gds_codes:
            print(x)
    
    print(hdr_info)

    act.expected_stdout = """
        Attributes full shutdown
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
