#coding:utf-8

"""
ID:          n/a
ISSUE:       n/a
TITLE:       DB with owner containing every character from string.punctuation set, with duplicating it up to max allowed length
DESCRIPTION:
    Test verifies ability to create DB with assigning to its OWNER values like  '!' * 63 ; '"' * 63 ; '<' * 63 etc.
    After such DB will be created (in empbedded mode), we check ability to create USER in it (via Services API).
    It is better to use self-security DB because later this test can be extented by some code that operates with another cases
    of extremely 'exotic' user names (i.e. such users must not remain in th default security.db if this test fails).
NOTES:
    [22.01.2026] pzotov
        There are several special characters for which logic of this test is changed:  backslash ; qouble quotes ; apostrophe.
        1. For backslash: we have to duplicate every TRAILING backslash because it is used as python escaping character.
           Because in this test OWNER contains only one character, we have to duplicate the whole OWNER name
           (all backslashes can be considered as 'trailing')
        2. For double quotes and apostrophe: currently one can not query SEC$USERS table when there is stored such owners.
           Attempt to do that (using cursor) will fail with:
               > raise self.__report(DatabaseError, self.status.get_errors())
               E firebird.driver.types.DatabaseError: Missing terminating quote <'> in the end of quoted string
               E -Secondary attachment - config data from DPB ignored
           As of double quotes, sec$users.sec$user_name contains 63 space characters after we add user = owner.
           (although SHOW DATABASE command issues `Owner: <63 double quotes here>`)
        3. Additionally:
            3.1. One need to be sure that firebird.conf does NOT contain DatabaseAccess = None.
            3.2. Value of REQUIRED_ALIAS must be EXACTLY the same as alias specified in the pre-created databases.conf
                 (for LINUX this equality is case-sensitive, even when aliases are compared!)
            3.3. Content of databases.conf must be taken from $QA_ROOT/files/qa-databases.conf
                 (one need to replace it before every test session).
                 Discussed with pcisar, letters since 30-may-2022 13:48.
    Checked on 6.0.0.1394 5.0.4.1746 4.0.7.3243.
"""
import random
import re
import string
import locale
from pathlib import Path
from firebird.driver import driver_config, DatabaseError, create_database, core as fb_core

import pytest
from firebird.qa import *

##############
REQUIRED_ALIAS = 'tmp_self_sec_alias'
CHECKED_CHARS_LST = list(string.punctuation)
##############

db = db_factory()
substitutions = []

act = python_act('db')

#--------------------------------------------------

def duplicate_trailing_backslashes_re(s):
    # Regex explanation:
    # (\\+)   - Captures one or more backslashes at the end of the string
    # $       - Asserts position at the end of the string
    # r'\1\1' - The replacement string, which doubles the captured group (group 1)
    return re.sub(r'(\\+)$', r'\1\1', s)

#--------------------------------------------------

@pytest.mark.version('>=4.0')
def test_1(act: Action, capsys):

    # Scan line-by-line through databases.conf, find line starting with REQUIRED_ALIAS and extract name of file that
    # must be created in the $(dir_sampleDb)/qa/ folder. This name will be used further as target database (tmp_fdb).
    # NOTE: we have to SKIP lines which are commented out, i.e. if they starts with '#':
    p_required_alias_ptn =  re.compile( '^(?!#)((^|\\s+)' + REQUIRED_ALIAS + ')\\s*=\\s*\\$\\(dir_sampleDb\\)/qa/', re.IGNORECASE )
    fname_in_dbconf = None

    MAX_USER_LENGTH = -1
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute("select f.rdb$character_length from rdb$fields f where f.rdb$field_name = 'RDB$USER'")
        MAX_USER_LENGTH = cur.fetchone()[0] # currently this is 63 on 4.x ... 6.x
    assert MAX_USER_LENGTH > 0

    with open(act.home_dir/'databases.conf', 'r') as f:
        for line in f:
            if p_required_alias_ptn.search(line):
                # If databases.conf contains line like this:
                #     tmp_core_6288_alias = $(dir_sampleDb)/qa/tmp_core_6038.fdb
                # - then we extract filename: 'tmp_qa_8253.fdb' (see below):
                fname_in_dbconf = Path(line.split('=')[1].strip()).name
                break

    # if 'fname_in_dbconf' remains undefined here then propably REQUIRED_ALIAS not equals to specified in the databases.conf!
    #
    assert fname_in_dbconf

    srv_cfg = """
        [local]
        host = localhost
        user = SYSDBA
        password = masterkey
    """
    srv_cfg = driver_config.register_server(name = 'test_db_owner_punct_chars', config = '')

    db_cfg_name = 'tmp_db_owner_punct_chars'
    db_cfg_object = driver_config.register_database(name = db_cfg_name)
    db_cfg_object.server.value = srv_cfg.name
    db_cfg_object.protocol.value = None
    db_cfg_object.database.value = REQUIRED_ALIAS

    tmp_fdb = Path( act.vars['sample_dir'], 'qa', fname_in_dbconf )

    chk_sql = """
        select
             lower(m.mon$database_name) as db_name
            ,m.mon$sec_database as sec_db
            ,trim(m.mon$owner) as db_owner_text
            ,octet_length(trim(m.mon$owner)) as db_owner_octets
            ,trim(a.mon$user) as whoami_text
            ,octet_length(trim(a.mon$user)) as whoami_octets
            ,a.mon$attachment_name as att_name
            ,s.sec$user_name as sec_user_text
            ,octet_length(trim(s.sec$user_name)) as sec_user_octets
        from mon$database m
        join mon$attachments a on a.mon$attachment_id = current_connection
        join sec$users s on upper(trim(s.sec$user_name)) = upper(trim(m.mon$owner))
    """
    
    expected_out_lines = []

    for k in range(len(CHECKED_CHARS_LST)):

        Path(tmp_fdb).unlink(missing_ok = True)

        db_owner = CHECKED_CHARS_LST[k] * MAX_USER_LENGTH
        db_owner = duplicate_trailing_backslashes_re(db_owner)

        # code from 'create-db-with-arbitrary-characters-in-its-owner.py'
        # DO NOT REMOVE IT!
        while len(db_owner) > MAX_USER_LENGTH:
            lst = list(db_owner)
            for i in range(len(lst)):
                if lst[i] == '\\':
                    pass
                else:
                    lst[i] = ''
                    break
            db_owner = ''.join(lst)
            if len(db_owner) > MAX_USER_LENGTH:
                db_owner = db_owner[:-1]

        db_owner = db_owner.replace('"', '""')

        db_passwd = '123'
        with create_database(db_cfg_name, user= f'"{db_owner}"', password = db_passwd) as con:
            cur = con.cursor()
            cur.execute('select mon$database_name as db_name from mon$database')
            ccol=cur.description
            self_db_file = '|TOTALLY|UNDEFINED|'
            for r in cur:
                for i in range(0,len(ccol)):
                    #print( ccol[i][0],':', r[i])
                    if ccol[i][0].lower() == 'db_name'.lower():
                        self_db_file = r[i].lower()
            con.commit()
        
            with fb_core.connect_server(server = srv_cfg.name, expected_db = self_db_file) as srv:
                svc = fb_core.ServerUserServices(srv)
                svc.add( user_name = f'"{db_owner}"', password = db_passwd, database = self_db_file)

            if CHECKED_CHARS_LST[k] in ('"', "'"):
                # Currently there is problem with executing query to security DB:
                # > for r in cur
                # ...
                # > raise self.__report(DatabaseError, self.status.get_errors())
                # E firebird.driver.types.DatabaseError: Missing terminating quote <'> in the end of quoted string
                # E -Secondary attachment - config data from DPB ignored
                pass
            else:
                cur.execute(chk_sql)
                ccol=cur.description
                for r in cur:
                    for i in range(0,len(ccol)):
                        print( ccol[i][0],':', r[i])
                add_block_to_expected_out = f"""
                    DB_NAME : {self_db_file}
                    SEC_DB : Self
                    DB_OWNER_TEXT : {db_owner}
                    DB_OWNER_OCTETS : {MAX_USER_LENGTH}
                    WHOAMI_TEXT : {db_owner}
                    WHOAMI_OCTETS : {MAX_USER_LENGTH}
                    ATT_NAME : tmp_self_sec_alias
                    SEC_USER_TEXT : {db_owner}
                    SEC_USER_OCTETS : {MAX_USER_LENGTH}
                """
                expected_out_lines.append(add_block_to_expected_out)
            con.drop_database()

    act.expected_stdout = '\n'.join(expected_out_lines)
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
