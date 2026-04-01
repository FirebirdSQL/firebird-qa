#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/8859
TITLE:       Services cannot work with user names containing space when embedded access is used
DESCRIPTION:
    Test uses pre-created databases.conf which has alias (see variable REQUIRED_ALIAS) and SecurityDatabase in its details
    which points to that alias, thus making such database be self-security.
    Database file for that alias must NOT exist in the QA_root/files/qa/ subdirectory: it will be created here.

    We create self-secutity DB using several cases for its owner names (see 'SELF_SEC_OWNERS_LST'):
        case-1: containing space, e.g.: john o'hara (such name MUST be enclosed in double quotes);
        case-2: name that looks like SQL identifier, e.g.: john_smith, -- but containing lowercase letters and thus
                it also must be enclosed in double quotes.
    We try to create self-secutity DB with appropriate owner and get full path of created DB, see 'self_sec_fdb'.
    Then we change state of this DB to 'full shutdown'.
    Finally, we make several attempts to bring this DB online, and on each iteration we make copy of this (self-sec) DB
    to some temporary file (see 'tmp_fdb') and try to bring it online via Services API and spicyfying appropriate owner name
    (see 'fbsvc_switches_lst' and act.svcmgr() invocations).
    No output must be issued by FBSVCMGR (which is called inside act.svcmgr()) and also no runtime error caused by QA-plugin
    must raise (e.g. "no permission for bring online access to database" if we specify wrong name of DB owner).
NOTES:
    [29.03.2026] pzotov
    1. One need to be sure that firebird.conf does NOT contain DatabaseAccess = None.
    2. Value of REQUIRED_ALIAS must be EXACTLY the same as alias specified in the pre-created databases.conf
       (for LINUX this equality is case-sensitive, even when aliases are compared!)
    3. Content of databases.conf must be taken from $QA_ROOT/files/qa-databases.conf (one need to replace it before every test session).
       Discussed with pcisar, letters since 30-may-2022 13:48, subject:
       "new qa, core_4964_test.py: strange outcome when use... shutil.copy() // comparing to shutil.copy2()"
    4. Ticket has been created after discussion with FB team, letters since 18.01.2026 1347, subj:
       "How to bring online self-security DB that has state 'full shutdown' - and use FBSVCMGR for that ?"

    Confirmed bug on 6.0.0.1835. got: "data base file name (o'hara) already given"
    Checked on 6.0.0.1850 SS/CS.
"""
import locale
import time
import re
import shutil
from pathlib import Path
import subprocess
import traceback

import pytest
from firebird.qa import *
from firebird.qa.plugin import ExecutionError

REQUIRED_ALIAS = 'tmp_gh_8859_alias'

db = db_factory()

act = python_act('db', substitutions=[('[ \t]+', ' ')])

tmp_fdb = temp_file('tmp_8859.check_for_ability_to_bring_online.fdb')
tmp_sql = temp_file('tmp_8859.sql') # for debug only

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_fdb: Path, tmp_sql: Path, capsys):

    # Scan line-by-line through databases.conf, find line starting with REQUIRED_ALIAS and extract name of file that
    # must be created in the $(dir_sampleDb)/qa/ folder. This name will be used further as target database (tmp_fdb).
    # NOTE: we have to SKIP lines which are commented out, i.e. if they starts with '#':
    p_required_alias_ptn =  re.compile( '^(?!#)((^|\\s+)' + REQUIRED_ALIAS + ')\\s*=\\s*\\$\\(dir_sampleDb\\)/qa/', re.IGNORECASE )
    fname_in_dbconf = None

    with open(act.home_dir/'databases.conf', 'r') as f:
        for line in f:
            if p_required_alias_ptn.search(line):
                # If databases.conf contains line like this:
                #     tmp_8859_alias = $(dir_sampleDb)/qa/tmp_qa_8859.fdb 
                # - then we extract filename: 'tmp_qa_8859.fdb' (see below):
                fname_in_dbconf = Path(line.split('=')[1].strip()).name
                break

    # if 'fname_in_dbconf' remains undefined here then propably REQUIRED_ALIAS not equals to specified in the databases.conf!
    #
    assert fname_in_dbconf
    
    #------------------------------------------------------

    ALTER_DBA_PSWD = 'alterkey'
    SELF_SEC_OWNERS_LST = ("john o'hara", "john_smith")
    for ss_owner in SELF_SEC_OWNERS_LST:
        init_ddl = f'''
            set bail on;
            set list on;
            set names utf8;
            create database '{REQUIRED_ALIAS}' user "{ss_owner}";
            create user "{ss_owner}" password '{ALTER_DBA_PSWD}' using plugin Srp;
            commit;
            connect 'localhost:{REQUIRED_ALIAS}' user "{ss_owner}" password '{ALTER_DBA_PSWD}';
            set count on;
            select
                d.mon$database_name as db_name
               ,d.mon$owner as mon_owner
               ,d.mon$sec_database as mon_sec_db
               ,s.sec$user_name as sec_user
               ,s.sec$plugin as sec_plugin
            from mon$database d
            left join sec$users s on s.sec$user_name = '{ss_owner.replace(chr(39), chr(39)+chr(39))}'
            ;
            commit;
        '''
        
        # tmp_sql.write_text(init_ddl, encoding = 'utf-8')
        act.isql(switches=['-q'], charset = 'utf8', input = init_ddl, credentials = False, connect_db = False, combine_output = True, io_enc = 'utf-8')

        assert 'db_name'.upper() in act.clean_stdout, f'{ss_owner=}. Output does not contain string with prefix = "DB_NAME":\n' + act.clean_stdout

        self_sec_fdb = [x.split()[1] for x in act.clean_stdout.splitlines() if x.startswith('db_name'.upper())][0]
        act.expected_stdout = f"""
            DB_NAME      {self_sec_fdb}
            MON_OWNER    {ss_owner}
            MON_SEC_DB   Self
            SEC_USER     {ss_owner}
            SEC_PLUGIN   Srp
            Records affected: 1
        """
        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()


        #--------------------------------------------------------------------------------------

        # C:`FB`60SS`gfix localhost:tmp_gh_8859_alias -user `""john o'hara"`" -pas alterkey -shut full -force 0
        act.gfix( switches = [ 'localhost:' + REQUIRED_ALIAS, '-user',  '"' + ss_owner + '"', '-pas', ALTER_DBA_PSWD, '-shut', 'full', '-force', '0'], credentials = False, combine_output = True, io_enc = locale.getpreferredencoding())
        assert act.clean_stdout == '' and act.return_code == 0
        act.reset()

        ############################################################
        ### CHECK THAT WE CAN BRING DB ONLINE USING SERVICES API ###
        ############################################################
        fbsvc_switches_lst = (
            [ 'service_mgr', 'user',  '"' + ss_owner + '"', 'action_properties', 'dbname', str(tmp_fdb), 'prp_db_online'],
            [ 'service_mgr', 'expected_db', REQUIRED_ALIAS, 'user', '"' + ss_owner + '"', 'action_properties', 'dbname', str(tmp_fdb), 'prp_db_online'],
        )
        # :: ok1 :: fbsvcmgr service_mgr user /""john o'hara"/" password alterkey action_properties dbname C:/temp/pytest/test_10/tmp_8859.check_for_ability_to_bring_online.fdb  prp_db_online
        
        for svc_params in fbsvc_switches_lst:
            tmp_fdb.unlink(missing_ok = True)
            shutil.copy2(self_sec_fdb, tmp_fdb)
            try:
                act.svcmgr( switches = svc_params, connect_mngr = False, io_enc = locale.getpreferredencoding())
                # 'no permission for bring online access to database' can raise here if we specify wrong name of DB owner
                if act.clean_stdout == '' and act.return_code == 0:
                    pass
                else:
                    print('FBSVCMGR: unexpected output for switches: ', ' '.join(svc_params) )
                    print(f'{act.clean_stdout=}')
                    print(f'{act.clean_stderr=}')
            except Exception as e:
                print('FBSVCMGR failed, switches: ', ' '.join(svc_params) )
                print(e.__class__)
                print(e.__str__())
                for p in traceback.format_exc().split('\n'):
                    if p.strip():
                        print('...',p)

            act.reset()
            assert '' == capsys.readouterr().out

        tmp_fdb.unlink(missing_ok = True)
        Path(self_sec_fdb).unlink()

    # < for ss_owner in enumerate(SELF_SEC_OWNERS_LST)
