#coding:utf-8

"""
ID:          issue-7046
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7046
TITLE:       Make ability to add comment to mapping ('COMMENT ON MAPPING ... IS ...')
DESCRIPTION:
    Test verifies ability to add comment both to local and global mappings.
    Also, it extracts metadata as SQL and checks presense of these comments there.
    In order to avoid remote connection to default security.db, we use pre-defined alias in the databases.conf,
    which points to SELF-SECURITY database that must be created in "$(dir_sampleDb)/qa/" directory. This folder
    is cleaned up before every test run, so we can be sure that it will not contain such database remaining from
    previous test session (see variable 'REQUIRED_ALIAS').

NOTES:
    [23.02.2023] pzotov
    1. One need to be sure that firebird.conf does NOT contain DatabaseAccess = None.
    2. Test uses pre-created databases.conf which has alias defined by variable REQUIRED_ALIAS.
       Database file for that alias must NOT exist in the QA_root/files/qa/ subdirectory: it will be created here.
       Content of databases.conf must be taken from $QA_ROOT/files/qa-databases.conf (one need to replace
       it before every test session).
       Discussed with pcisar, letters since 30-may-2022 13:48, subject:
       "new qa, core_4964_test.py: strange outcome when use... shutil.copy() // comparing to shutil.copy2()"
    3. Value of REQUIRED_ALIAS must be EXACTLY the same as alias specified in the pre-created databases.conf
       (for LINUX this equality is case-sensitive, even when aliases are compared!)

    ::: NB-1 :::
    CURRENTLY comment for mapping is NOT shown when we extract metadata using isql -x.
    Because of that, only comment for VIEW is specified in expected text.
    Test will be asjusted after this issue will be fixed.

    ::: NB-2 :::
    Ability to specify non-ascii comment to mapping was not checked.
    
    Checked on 5.0.0.958
"""

import os
import re
import locale
import subprocess
from pathlib import Path
import time

import pytest
from firebird.qa import *

# Name of alias for self-security DB in the QA_root/files/qa-databases.conf.
# This file must be copied manually to each testing FB homw folder, with replacing
# databases.conf there:
#
REQUIRED_ALIAS = 'tmp_gh_7046_alias'

db = db_factory()
act = python_act('db', substitutions=[('[ \t]+', ' '), ('.*===.*', ''), ('PLUGIN .*', 'PLUGIN'), ('MAP_COMMENT_BLOB_ID .*', 'MAP_COMMENT_BLOB_ID')])

fn_meta_log = temp_file('tmp_gh_7046-meta.log')
fn_meta_err = temp_file('tmp_gh_7046-meta.err')

@pytest.mark.version('>=5.0')
def test_1(act: Action, fn_meta_log: Path, fn_meta_err: Path, capsys):
    
    # Scan line-by-line through databases.conf, find line starting with REQUIRED_ALIAS and extract name of file that
    # must be created in the $(dir_sampleDb)/qa/ folder. This name will be used further as target database (tmp_fdb).
    # NOTE: we have to SKIP lines which are commented out, i.e. if they starts with '#':
    p_required_alias_ptn =  re.compile( '^(?!#)((^|\\s+)' + REQUIRED_ALIAS + ')\\s*=\\s*\\$\\(dir_sampleDb\\)/qa/', re.IGNORECASE )
    fname_in_dbconf = None

    with open(act.home_dir/'databases.conf', 'r') as f:
        for line in f:
            if p_required_alias_ptn.search(line):
                # If databases.conf contains line like this:
                #     tmp_7046_alias = $(dir_sampleDb)/qa/tmp_gh_7046.fdb
                # - then we extract filename: 'tmp_gh_7046.fdb' (see below):
                fname_in_dbconf = Path(line.split('=')[1].strip()).name
                break

    # if 'fname_in_dbconf' remains undefined here then propably REQUIRED_ALIAS not equals to specified in the databases.conf!
    #
    assert fname_in_dbconf

    # Full path + filename of database to which we will try to connect:
    #
    tmp_fdb = Path( act.vars['sample_dir'], 'qa', fname_in_dbconf )

    PLUGIN_FOR_MAPPING = 'Srp'
    MAPPING_NAME = 'trusted_auth_7046'

    # UnicodeEncodeError: charmap codec cant encode characters in position 601-605: character maps to <undefined>
    MAPPING_COMMENT = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua'
    VIEW_COMMENT = 'Audiam legimus mei an, eu possit constituto per, case assentior te usu'

    sql_txt = f'''
        set bail on;
        set list on;
        set blob all;
        create database '{REQUIRED_ALIAS}' user {act.db.user};
        select
            m.mon$sec_database as mon_sec_db
        from mon$database m;
        commit;

        create or alter global mapping {MAPPING_NAME} using plugin {PLUGIN_FOR_MAPPING} from any user to user;
        commit;
        comment on mapping {MAPPING_NAME} is '{MAPPING_COMMENT}';
        commit;


        recreate view v_map_info as
        select
            map_name
           ,map_type
           -- ,map_plugin
           ,from_type
           ,map_from
           ,to_type
           ,map_to
           ,map_comment_blob_id
        from
        (
            select
                 'LOCAL'           as map_type
                ,rdb$map_name      as map_name
                ,rdb$map_plugin    as map_plugin
                ,rdb$map_from_type as from_type
                ,rdb$map_from      as map_from
                ,rdb$map_to_type   as to_type
                ,rdb$map_to        as map_to
                ,rdb$description   as map_comment_blob_id
            from rdb$auth_mapping
            UNION ALL
            select
                 'GLOBAL'
                ,sec$map_name
                ,sec$map_plugin
                ,sec$map_from_type
                ,sec$map_from
                ,sec$map_to_type
                ,sec$map_to
                ,sec$description
            from sec$global_auth_mapping
        ) t
        where
            t.map_name = upper('{MAPPING_NAME}')
            and upper(t.map_plugin) = upper('{PLUGIN_FOR_MAPPING}')
        ;
        commit;
        comment on view v_map_info is '{VIEW_COMMENT}';
        commit;

        set count on;
        select * from v_map_info;
        quit;
    '''

    expected_stdout_isql = f'''
        MON_SEC_DB Self

        MAP_NAME TRUSTED_AUTH_7046
        MAP_TYPE LOCAL
        FROM_TYPE USER
        MAP_FROM *
        TO_TYPE 0
        MAP_TO <null>
        MAP_COMMENT_BLOB_ID 2d:1e0
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua

        MAP_NAME TRUSTED_AUTH_7046
        MAP_TYPE GLOBAL
        FROM_TYPE USER
        MAP_FROM *
        TO_TYPE 0
        MAP_TO <null>
        MAP_COMMENT_BLOB_ID 0:2
        Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua

        Records affected: 2
    '''

    try:
        act.expected_stdout = expected_stdout_isql
        act.isql(switches = ['-q'], input = sql_txt, connect_db=False, credentials = False, combine_output = True, io_enc = locale.getpreferredencoding(), charset = 'utf8')

        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()
        

        with fn_meta_log.open(mode='w') as meta_out, fn_meta_err.open(mode='w') as meta_err:
            # could not find how properly call act.extract_meta with ANOTHER database (different from currently created).
            subprocess.call( [ act.vars['isql'],'-x', '-user', act.db.user, '-pas', act.db.password, REQUIRED_ALIAS ], 
                             stdout = meta_out,
                             stderr = meta_err
                           )

        for g in (fn_meta_log, fn_meta_err):
            with g.open() as f:
                for line in f:
                    if line.split():
                        if g == fn_meta_log:
                            if ' MAPPING ' in line or 'COMMENT ON ' in line:
                                print(f'{line}')
                        else:
                            print(f'UNEXPECTED MATADATA STDOUT: {line}')

        act.expected_stdout = f"""
            CREATE MAPPING {MAPPING_NAME.upper()} USING PLUGIN
            CREATE OR ALTER GLOBAL MAPPING {MAPPING_NAME.upper()} USING PLUGIN
            COMMENT ON VIEW V_MAP_INFO IS '{VIEW_COMMENT}';
        """

    finally:
        tmp_fdb.unlink()
    
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
