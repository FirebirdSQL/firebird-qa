#coding:utf-8

"""
ID:          issue-9077
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9077
TITLE:       Services API gbak does not provide support for -SKIP_SCHEMA_DATA/-INCLUDE_SCHEMA_DATA equivalent options
DESCRIPTION:
    Test creates three schemas (besides PUBLIC: S_REQUIRED, S_AUX_DATA, S_OPTIONAL) and three tables in each of them ("T_" with same suffixes).
    Then we do full backup of test database in order to check further results of restore with diff options.

    After this we check logs of backup that is performed using fbsvcmgr and use BKP_INCLUDE* and BKP_SKIP* command switches.
    Finally, we repeat same steps with restore action and again check logs.
    Each logs must have:
        * BACKUP:
            gbak:skipping data for table <schema>.<name>
        * RESTORE:
            gbak:skipping data for table <schema>.<name>
            gbak: <NNNN> records ignored
    NB: log of backup must NOT have line with number of skipped records, as noted by Alex:
    https://github.com/FirebirdSQL/firebird/issues/9077#issuecomment-4927356727 
NOTES:
    [09.08.2026] pzotov
    ::: NOTE ::: TEST CONTAINS TWO ASSERTS!
    Confirmed bug on 6.0.0.2035-f276111, got: "Invalid clumplet buffer structure: unknown parameter for backup/restore (23)"
    Checked on 6.0.0.2126-a8b87b4.
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
    create table t_aux_data(id int);
    create table t_optional(id int);

    create schema s_required;
    create schema s_aux_data;
    create schema s_optional;

    create table s_required.t_required(id int);
    create table s_required.t_aux_data(id int);
    create table s_required.t_optional(id int);

    create table s_aux_data.t_required(id int);
    create table s_aux_data.t_aux_data(id int);
    create table s_aux_data.t_optional(id int);

    create table s_optional.t_required(id int);
    create table s_optional.t_aux_data(id int);
    create table s_optional.t_optional(id int);
    commit;

    insert into t_required(id) select i from generate_series(1, {NUM_ROWS}) as s(i);
    insert into t_aux_data(id) select id from t_required;
    insert into t_optional(id) select id from t_required;

    insert into s_required.t_required(id) select id from t_required;
    insert into s_required.t_aux_data(id) select id from t_required;
    insert into s_required.t_optional(id) select id from t_required;

    insert into s_optional.t_required(id) select id from t_required;
    insert into s_optional.t_aux_data(id) select id from t_required;
    insert into s_optional.t_optional(id) select id from t_required;
    commit;
"""

db = db_factory(init = init_script, charset = 'utf8')
act = python_act('db', substitutions=substitutions)

tmp_fdb = temp_file('tmp_gh_9077.fdb')
tmp_fbk = temp_file('tmp_gh_9077.fbk')
tmp_log = temp_file('tmp_gh_9077.log')

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_fdb: Path, tmp_fbk: Path, tmp_log: Path, capsys):

    br_map = \
    {
        ( 'fbsvcmgr', 'backup', 'incl_table'    ) : ( 'bkp_include_data',        't_required'.upper() ),
        ( 'fbsvcmgr', 'backup', 'incl_schema'   ) : ( 'bkp_include_schema_data', 's_required'.upper() ),
        ( 'fbsvcmgr', 'backup', 'skip_table'    ) : ( 'bkp_skip_data',           't_optional'.upper() ),
        ( 'fbsvcmgr', 'backup', 'skip_schema'   ) : ( 'bkp_skip_schema_data',    's_optional'.upper() ),
        
        ( 'fbsvcmgr', 'restore', 'incl_table'   ) : ( 'res_include_data',        't_required'.upper() ),
        ( 'fbsvcmgr', 'restore', 'incl_schema'  ) : ( 'res_include_schema_data', 's_required'.upper() ),
        ( 'fbsvcmgr', 'restore', 'skip_table'   ) : ( 'res_skip_data',           't_optional'.upper() ),
        ( 'fbsvcmgr', 'restore', 'skip_schema'  ) : ( 'res_skip_schema_data',    's_optional'.upper() ),
    }

    # ::::::::::::::::::::::::::::::::::::::::::
    # ::: c h e c k    b a c k u p    l o g  :::
    # ::::::::::::::::::::::::::::::::::::::::::
    for k,v in {k:v for k,v in br_map.items() if k[1] == 'backup'}.items():
        util, mode, skip_type = k[:3]
        cmd_key, cmd_val = v[:2] 
        if util == 'gbak':
            act.gbak(switches = ['-b', act.db.dsn, str(tmp_fbk), '-verbose', cmd_key, cmd_val], combine_output = True, io_enc = locale.getpreferredencoding())
        else:
            act.svcmgr(switches = ['action_backup', 'dbname', act.db.db_path, 'bkp_file', tmp_fbk, 'verbose', cmd_key, cmd_val] )
        
        matches = re.findall(r"^gbak:skipping data for table \S+", act.clean_stdout, flags=re.MULTILINE)
        if matches:
            print(f"Doing {mode.upper()} using {util=}, {cmd_key=}, {cmd_val=}:")
            for p in matches:
                print(p)
        else:
            print(f"Doing {mode.upper()} using {util=}, {cmd_key=}, {cmd_val=}: could not find any matching line. Check entire log:")
            for line in act.clean_stdout.splitlines():
                print(line)
        act.reset()


    act.expected_stdout = f"""
        Doing BACKUP using util='fbsvcmgr', cmd_key='bkp_include_data', cmd_val='T_REQUIRED':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak:skipping data for table "S_OPTIONAL"."T_AUX_DATA"
        gbak:skipping data for table "S_AUX_DATA"."T_OPTIONAL"
        gbak:skipping data for table "S_AUX_DATA"."T_AUX_DATA"
        gbak:skipping data for table "S_REQUIRED"."T_OPTIONAL"
        gbak:skipping data for table "S_REQUIRED"."T_AUX_DATA"
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        gbak:skipping data for table "PUBLIC"."T_AUX_DATA"
        
        Doing BACKUP using util='fbsvcmgr', cmd_key='bkp_include_schema_data', cmd_val='S_REQUIRED':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak:skipping data for table "S_OPTIONAL"."T_AUX_DATA"
        gbak:skipping data for table "S_OPTIONAL"."T_REQUIRED"
        gbak:skipping data for table "S_AUX_DATA"."T_OPTIONAL"
        gbak:skipping data for table "S_AUX_DATA"."T_AUX_DATA"
        gbak:skipping data for table "S_AUX_DATA"."T_REQUIRED"
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        gbak:skipping data for table "PUBLIC"."T_AUX_DATA"
        gbak:skipping data for table "PUBLIC"."T_REQUIRED"
        
        Doing BACKUP using util='fbsvcmgr', cmd_key='bkp_skip_data', cmd_val='T_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak:skipping data for table "S_AUX_DATA"."T_OPTIONAL"
        gbak:skipping data for table "S_REQUIRED"."T_OPTIONAL"
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        
        Doing BACKUP using util='fbsvcmgr', cmd_key='bkp_skip_schema_data', cmd_val='S_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak:skipping data for table "S_OPTIONAL"."T_AUX_DATA"
        gbak:skipping data for table "S_OPTIONAL"."T_REQUIRED"
    """
    act.stdout = capsys.readouterr().out

    ###########################
    ###   a s s e r t - 1   ###
    ###########################
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
    for k,v in {k:v for k,v in br_map.items() if k[1] == 'restore'}.items():
        util, mode, skip_type = k[:3]
        cmd_key, cmd_val = v[:2] 
        if util == 'gbak':
            act.gbak(switches = ['-rep', str(tmp_fbk), str(tmp_fdb), '-verbose', cmd_key, cmd_val ], combine_output = True, io_enc = locale.getpreferredencoding())
        else:
            act.svcmgr(switches = ['action_restore', 'bkp_file', tmp_fbk, 'dbname', act.db.db_path, 'res_replace', 'verbose', cmd_key, cmd_val] )

        #matches = re.findall(r"^gbak:skipping data for table \S+", act.clean_stdout, flags=re.MULTILINE)
        matches = re.findall(r"^gbak:skipping data for table \S+\s*\ngbak:\s+\d+ records? ignored", act.clean_stdout, flags=re.MULTILINE)
        if matches:
            print(f"Doing {mode.upper()} using {util=}, {cmd_key=}, {cmd_val=}:")
            for p in matches:
                print(p)
        else:
            print(f"Doing {mode.upper()} using {util=}, {cmd_key=}, {cmd_val=}: could not find any matching line. Check entire log:")
            for line in act.clean_stdout.splitlines():
                print(line)
        act.reset()

    act.expected_stdout = f"""
        Doing RESTORE using util='fbsvcmgr', cmd_key='res_include_data', cmd_val='T_REQUIRED':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_OPTIONAL"."T_AUX_DATA"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_REQUIRED"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_REQUIRED"."T_AUX_DATA"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "PUBLIC"."T_AUX_DATA"
        gbak: {NUM_ROWS} records ignored
        
        Doing RESTORE using util='fbsvcmgr', cmd_key='res_include_schema_data', cmd_val='S_REQUIRED':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_OPTIONAL"."T_AUX_DATA"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_OPTIONAL"."T_REQUIRED"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "PUBLIC"."T_AUX_DATA"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "PUBLIC"."T_REQUIRED"
        gbak: {NUM_ROWS} records ignored
        
        Doing RESTORE using util='fbsvcmgr', cmd_key='res_skip_data', cmd_val='T_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_REQUIRED"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "PUBLIC"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        
        Doing RESTORE using util='fbsvcmgr', cmd_key='res_skip_schema_data', cmd_val='S_OPTIONAL':
        gbak:skipping data for table "S_OPTIONAL"."T_OPTIONAL"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_OPTIONAL"."T_AUX_DATA"
        gbak: {NUM_ROWS} records ignored
        gbak:skipping data for table "S_OPTIONAL"."T_REQUIRED"
        gbak: {NUM_ROWS} records ignored
    """
    act.stdout = capsys.readouterr().out
    ###########################
    ###   a s s e r t - 2   ###
    ###########################
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
