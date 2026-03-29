#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8903
TITLE:       Use of some switches with parameter in gbak's command line before name of database in -SE mode breaks access to databases with non-default security database
DESCRIPTION:
    Test uses pre-created databases.conf which has alias (see variable REQUIRED_ALIAS) and SecurityDatabase in its details
    which points to that alias, thus making such database be self-security.
    Database file for that alias must NOT exist in the QA_root/files/qa/ subdirectory: it will be created here.
NOTES:
    [29.03.2026] pzotov
    1. One need to be sure that firebird.conf does NOT contain DatabaseAccess = None.
    2. Value of REQUIRED_ALIAS must be EXACTLY the same as alias specified in the pre-created databases.conf
       (for LINUX this equality is case-sensitive, even when aliases are compared!)
    3. Content of databases.conf must be taken from $QA_ROOT/files/qa-databases.conf (one need to replace it before every test session).
       Discussed with pcisar, letters since 30-may-2022 13:48, subject:
       "new qa, core_4964_test.py: strange outcome when use... shutil.copy() // comparing to shutil.copy2()"

    Confirmed bug on 6.0.0.1819-61354ae, 5.0.4.1783-efed600.
    Checked on 6.0.0.1824-c7ba4ca, 5.0.4.1784-6f02f0a.
"""
import locale
import re
from pathlib import Path

import pytest
from firebird.qa import *

REQUIRED_ALIAS = 'tmp_gh_8903_alias'

db = db_factory()

act = python_act('db', substitutions=[('[ \t]+', ' ')])

tmp_fbk = temp_file('tmp_8903.fbk')

@pytest.mark.version('>=5.0.4')
def test_1(act: Action, tmp_fbk: Path, capsys):

    # Scan line-by-line through databases.conf, find line starting with REQUIRED_ALIAS and extract name of file that
    # must be created in the $(dir_sampleDb)/qa/ folder. This name will be used further as target database (tmp_fdb).
    # NOTE: we have to SKIP lines which are commented out, i.e. if they starts with '#':
    p_required_alias_ptn =  re.compile( '^(?!#)((^|\\s+)' + REQUIRED_ALIAS + ')\\s*=\\s*\\$\\(dir_sampleDb\\)/qa/', re.IGNORECASE )
    fname_in_dbconf = None

    with open(act.home_dir/'databases.conf', 'r') as f:
        for line in f:
            if p_required_alias_ptn.search(line):
                # If databases.conf contains line like this:
                #     tmp_8903_alias = $(dir_sampleDb)/qa/tmp_qa_8903.fdb 
                # - then we extract filename: 'tmp_qa_8903.fdb' (see below):
                fname_in_dbconf = Path(line.split('=')[1].strip()).name
                break

    # if 'fname_in_dbconf' remains undefined here then propably REQUIRED_ALIAS not equals to specified in the databases.conf!
    #
    assert fname_in_dbconf

    ALTER_DBA_PSWD = 'alterkey'
    init_ddl = f'''
        set bail on;
        set list on;
        create database '{REQUIRED_ALIAS}' user {act.db.user};
        create user {act.db.user} password '{ALTER_DBA_PSWD}';
        commit;
        connect 'localhost:{REQUIRED_ALIAS}' user {act.db.user} password '{ALTER_DBA_PSWD}';
        select mon$sec_database from mon$database; -- must be: 'Self'
        commit;
    '''
    act.isql(switches=['-q'], input = init_ddl, credentials = False, connect_db = False, combine_output = True, io_enc = locale.getpreferredencoding())

    act.expected_stdout = f"""
        MON$SEC_DATABASE Self
    """
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

    #--------------------------------------------------------------------------------------

    # gbak -se localhost:service_mgr -par 2 -b -g -m -user SYSDBA -pass sys_8903_dba tmp_gh_8903_alias /path/ti/gh-8903-ini.fbk 
    act.gbak( switches = [ '-se', 'localhost:service_mgr', '-par', '2', '-b', '-g', '-m', '-user', act.db.user, '-pass', ALTER_DBA_PSWD, REQUIRED_ALIAS, tmp_fbk ]
              ,combine_output = True
              ,io_enc = locale.getpreferredencoding()
            )
    assert act.clean_stdout == '' and act.return_code == 0
