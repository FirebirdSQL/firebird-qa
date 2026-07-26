#coding:utf-8

"""
ID:          issue-9075
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9075
TITLE:       Improve gbak logging of ignored records with skip/include (schema) data by mentioning the table name
DESCRIPTION:
    Test creates several schemas (besides PUBLIC) and two tables in each of them.
    Then we do backup and run restore two times with '-SKIP_DATA' and '-SKIP_SCHEMA_DATA' command switches.
    First time we require to skip data of TABLE with name 'T_OPTIONAL', second time - all objects from schema 'S_OPTIONAL'.
    Each logs must have:
        * BACKUP:
            gbak:skipping data for table <schema>.<name>
        * RESTORE:
            gbak:skipping data for table <schema>.<name>
            gbak: <NNNN> records ignored
    NB: log of backup must NOT have line with number of skipped records, as noted by Alex:
    https://github.com/FirebirdSQL/firebird/issues/9075#issuecomment-4927356727 
NOTES:
    [09.07.2026] pzotov
        Currently only log of *restore* contains info about names of skipped DB objects. This is not so for BACKUP log.
        See https://github.com/FirebirdSQL/firebird/issues/9075#issuecomment-4926599975
        Test probably will be changed later.
        Confirmed improvement on 6.0.0.2070-d2cb23c.
    [26.07.2026] pzotov
        Log of BACKUP now also contains info about skipped tables/schemas, see:
        https://github.com/FirebirdSQL/firebird/commit/7b248ddfcf3e89b0d07b71c288748c6d4cbdc98e
        Test has been refactored: both logs are checked (backup + restore), and this is done both for GBAK and FBSVCMGR.
        Checked on 6.0.0.2092-3fa7269 (commit timestamp: 25.07.2026 19:42).
"""
import re
import locale
from pathlib import Path

import pytest
from firebird.qa import *

substitutions = [('[ \t]+', ' '), ]

NUM_ROWS = 10000
init_script = f"""
    create table t_required(id int);
    create table t_optional(id int);

    create schema s_required;
    create schema s_optional;

    create table s_required.t_required(id int);
    create table s_required.t_optional(id int);

    create table s_optional.t_required(id int);
    create table s_optional.t_optional(id int);
    commit;

    insert into t_required(id) select i from generate_series(1, {NUM_ROWS}) as s(i);
    insert into t_optional(id) select id from t_required;

    insert into s_required.t_required(id) select id from t_required;
    insert into s_required.t_optional(id) select id from t_required;

    insert into s_optional.t_required(id) select id from t_required;
    insert into s_optional.t_optional(id) select id from t_required;
    commit;
"""

db = db_factory(init = init_script)
act = python_act('db', substitutions=substitutions)

tmp_fdb = temp_file('tmp_gh_9075.fdb')
tmp_fbk = temp_file('tmp_gh_9075.fbk')
tmp_log = temp_file('tmp_gh_9075.log')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_fdb: Path, tmp_fbk: Path, tmp_log: Path, capsys):

    skip_map = \
    {
        ( 'gbak',     'backup', 'skip_table'    ) : ( '-skip_data',           't_optional'.upper() ),
        ( 'gbak',     'backup', 'skip_schema'   ) : ( '-skip_schema_data',    's_optional'.upper() ),
        ( 'fbsvcmgr', 'backup', 'skip_table'    ) : ( 'bkp_skip_data',        't_optional'.upper() ),
        ( 'fbsvcmgr', 'backup', 'skip_schema'   ) : ( 'bkp_skip_schema_data', 's_optional'.upper() ),

        ( 'gbak',     'restore', 'skip_table'   ) : ( '-skip_data',           't_optional'.upper() ),
        ( 'gbak',     'restore', 'skip_schema'  ) : ( '-skip_schema_data',    's_optional'.upper() ),
        ( 'fbsvcmgr', 'restore', 'skip_table'   ) : ( 'res_skip_data',        't_optional'.upper() ),
        ( 'fbsvcmgr', 'restore', 'skip_schema'  ) : ( 'res_skip_schema_data', 's_optional'.upper() ),
    }

    # ::::::::::::::::::::::::::::::::::::::::::
    # ::: c h e c k    b a c k u p    l o g  :::
    # ::::::::::::::::::::::::::::::::::::::::::
    for k,v in {k:v for k,v in skip_map.items() if k[1] == 'backup'}.items():
        util, mode, skip_type = k[:3]
        skip_key, skip_val = v[:2] 
        if util == 'gbak':
            act.gbak(switches = ['-b', act.db.dsn, str(tmp_fbk), '-verbose', skip_key, skip_val], combine_output = True, io_enc = locale.getpreferredencoding())
        else:
            act.svcmgr(switches = ['action_backup', 'dbname', act.db.db_path, 'bkp_file', tmp_fbk, 'verbose', skip_key, skip_val] )
        matches = re.findall(r"^gbak:skipping data for table \S+", act.clean_stdout, flags=re.MULTILINE)
        if matches:
            print(f"Doing {mode.upper()} using {util=}, {skip_key=}, {skip_val=}:")
            for p in matches:
                print(p)
        else:
            print(f"Doing {mode.upper()} using {util=}, {skip_key=}, {skip_val=}: could not find any matching line. Check entire log:")
            for line in act.clean_stdout.splitlines():
                print(line)
        act.reset()

    act.expected_stdout = f"""
        Doing BACKUP using util='gbak', skip_key='-skip_data', skip_val='T_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak:skipping data for table "S_REQUIRED"."T_OPTIONAL"
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        
        Doing BACKUP using util='gbak', skip_key='-skip_schema_data', skip_val='S_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak:skipping data for table "S_OPTIONAL"."T_REQUIRED"
        
        Doing BACKUP using util='fbsvcmgr', skip_key='bkp_skip_data', skip_val='T_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak:skipping data for table "S_REQUIRED"."T_OPTIONAL"
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        
        Doing BACKUP using util='fbsvcmgr', skip_key='bkp_skip_schema_data', skip_val='S_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak:skipping data for table "S_OPTIONAL"."T_REQUIRED"
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()

    #....................................................
    # Now we have to make *full* backup in order to check further RESTORE outcome (logs for '-skip' options):
    act.gbak(switches=['-b', act.db.dsn, str(tmp_fbk) ], combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.return_code ==0 and act.clean_stdout == ''
    act.reset()
    #....................................................
        
    # ::::::::::::::::::::::::::::::::::::::::::
    # ::: c h e c k   r e s t o r e   l o g  :::
    # ::::::::::::::::::::::::::::::::::::::::::
    for k,v in {k:v for k,v in skip_map.items() if k[1] == 'restore'}.items():
        util, mode, skip_type = k[:3]
        skip_key, skip_val = v[:2] 
        if util == 'gbak':
            act.gbak(switches = ['-rep', str(tmp_fbk), str(tmp_fdb), '-verbose', skip_key, skip_val ], combine_output = True, io_enc = locale.getpreferredencoding())
        else:
            act.svcmgr(switches = ['action_restore', 'bkp_file', tmp_fbk, 'dbname', act.db.db_path, 'res_replace', 'verbose', skip_key, skip_val] )

        #matches = re.findall(r"^gbak:skipping data for table \S+", act.clean_stdout, flags=re.MULTILINE)
        matches = re.findall(r"^gbak:skipping data for table \S+\s*\ngbak:\s+\d+ records? ignored", act.clean_stdout, flags=re.MULTILINE)
        if matches:
            print(f"Doing {mode.upper()} using {util=}, {skip_key=}, {skip_val=}:")
            for p in matches:
                print(p)
        else:
            print(f"Doing {mode.upper()} using {util=}, {skip_key=}, {skip_val=}: could not find any matching line. Check entire log:")
            for line in act.clean_stdout.splitlines():
                print(line)
        act.reset()

    act.expected_stdout = f"""
        Doing RESTORE using util='gbak', skip_key='-skip_data', skip_val='T_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_REQUIRED"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        
        Doing RESTORE using util='gbak', skip_key='-skip_schema_data', skip_val='S_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_OPTIONAL"."T_REQUIRED"
        gbak: {NUM_ROWS} records ignored
        
        Doing RESTORE using util='fbsvcmgr', skip_key='res_skip_data', skip_val='T_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_REQUIRED"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        
        Doing RESTORE using util='fbsvcmgr', skip_key='res_skip_schema_data', skip_val='S_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_OPTIONAL"."T_REQUIRED"
        gbak: {NUM_ROWS} records ignored
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
