#coding:utf-8

"""
ID:          issue-2170
ISSUE:       2170
TITLE:       Expression index can be created while doing inserts into table
DESCRIPTION:
  We check three cases of Tx setting: WAIT, NO WAIT and LOCK TIMEOUT n.

  First ISQL session always inserts some number of rows and falls in delay (it is created
  artificially by attempting to insert duplicate key in index in Tx with lock timeout = 7).

  Second ISQL is launched in SYNC mode after small delay (3 seconds) and starts transaction
  with corresponding WAIT/NO WAIT/LOCK TIMEOUT clause.

  If Tx starts with NO wait or lock timeout then this (2nd) ISQL always MUST FAIL.

  After 2nd ISQL will finish, we have to wait yet 5 seconds for 1st ISQL will gone.
  Total time of these two delays (3+5=8) must be greater than lock timeout in the script which
  is running by 1st ISQL (7 seconds).

  Initial version of this test did use force interruption of both ISQL processes but this was unneeded,
  though it helped to discover some other bug in engine which produced bugcheck - see CORE-5275.
NOTES:
[15.1.2022] pcisar
  This test may FAIL when run on slow machine (like VM), or fast one (Windows 10 with SSD)
JIRA:        CORE-1746
FBTEST:      bugs.core_1746
"""

import pytest
import time
import subprocess
from pathlib import Path
from firebird.qa import *

substitutions = [('0: CREATE INDEX LOG: RDB_EXPR_BLOB.*', '0: CREATE INDEX LOG: RDB_EXPR_BLOB'),
                 ('BULK_INSERT_START.*', 'BULK_INSERT_START'),
                 ('BULK_INSERT_FINISH.*', 'BULK_INSERT_FINISH'),
                 ('CREATE_INDX_START.*', 'CREATE_INDX_START'),
                 ('AFTER LINE.*', 'AFTER LINE')]

init_script = """
    create or alter procedure sp_ins(n int) as begin end;

    recreate table test(x int unique using index test_x, s varchar(10) default 'qwerty' );

    set term  ^;
    execute block as
    begin
        execute statement 'drop sequence g';
        when any do begin end
    end
    ^
    set term ;^
    commit;
    create sequence g;
    commit;

    set term ^;
    create or alter procedure sp_ins(n int) as
    begin
        while (n>0) do
        begin
            insert into test( x ) values( gen_id(g,1) );
            n = n - 1;
        end
    end
    ^
    set term ;^
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db', substitutions=substitutions)

tmp_file_bi_in = temp_file('bulk_insert.sql')
tmp_file_bi_out = temp_file('bulk_insert.out')

expected_stdout = """
    0: BULK INSERTS LOG: BULK_INSERT_START
    0: BULK INSERTS LOG: BULK_INSERT_FINISH
    0: CREATE INDEX LOG: INSERTS_STATE                   OK, IS RUNNING
    0: CREATE INDEX LOG: CREATE_INDX_START
    0: CREATE INDEX LOG: SET TRANSACTION WAIT;
    0: CREATE INDEX LOG: CREATE INDEX TEST_WAIT ON TEST COMPUTED BY('WAIT'|| S);
    0: CREATE INDEX LOG: COMMIT;
    0: CREATE INDEX LOG: SET ECHO OFF;
    0: CREATE INDEX LOG: INSERTS_STATE                   OK, FINISHED
    0: CREATE INDEX LOG: RDB$INDEX_NAME                  TEST_WAIT
    0: CREATE INDEX LOG: RDB$UNIQUE_FLAG                 0
    0: CREATE INDEX LOG: RDB$INDEX_INACTIVE              0
    0: CREATE INDEX LOG: RDB_EXPR_BLOB
    0: CREATE INDEX LOG: ('WAIT'|| S)
    0: CREATE INDEX LOG: RECORDS AFFECTED: 1
    0: CREATE INDEX LOG: SET PLAN ON;
    0: CREATE INDEX LOG: SELECT 1 FROM TEST WHERE 'WAIT'|| S > '' ROWS 0;
    0: CREATE INDEX LOG: PLAN (TEST INDEX (TEST_WAIT))
    0: CREATE INDEX LOG: SET PLAN OFF;
    0: CREATE INDEX LOG: SET ECHO OFF;

    1: BULK INSERTS LOG: BULK_INSERT_START
    1: BULK INSERTS LOG: BULK_INSERT_FINISH
    1: CREATE INDEX LOG: INSERTS_STATE                   OK, IS RUNNING
    1: CREATE INDEX LOG: CREATE_INDX_START
    1: CREATE INDEX LOG: SET TRANSACTION NO WAIT;
    1: CREATE INDEX LOG: CREATE INDEX TEST_NO_WAIT ON TEST COMPUTED BY('NO_WAIT'|| S);
    1: CREATE INDEX LOG: COMMIT;
    1: CREATE INDEX LOG: STATEMENT FAILED, SQLSTATE = 40001
    1: CREATE INDEX LOG: LOCK CONFLICT ON NO WAIT TRANSACTION
    1: CREATE INDEX LOG: -UNSUCCESSFUL METADATA UPDATE
    1: CREATE INDEX LOG: -OBJECT TABLE "TEST" IS IN USE

    2: BULK INSERTS LOG: BULK_INSERT_START
    2: BULK INSERTS LOG: BULK_INSERT_FINISH
    2: CREATE INDEX LOG: INSERTS_STATE                   OK, IS RUNNING
    2: CREATE INDEX LOG: CREATE_INDX_START
    2: CREATE INDEX LOG: SET TRANSACTION LOCK TIMEOUT 1;
    2: CREATE INDEX LOG: CREATE INDEX TEST_LOCK_TIMEOUT_1 ON TEST COMPUTED BY('LOCK_TIMEOUT_1'|| S);
    2: CREATE INDEX LOG: COMMIT;
    2: CREATE INDEX LOG: STATEMENT FAILED, SQLSTATE = 40001
    2: CREATE INDEX LOG: LOCK TIME-OUT ON WAIT TRANSACTION
    2: CREATE INDEX LOG: -UNSUCCESSFUL METADATA UPDATE
    2: CREATE INDEX LOG: -OBJECT TABLE "TEST" IS IN USE
"""

@pytest.mark.skip("FIXME: see notes")
@pytest.mark.version('>=3')
def test_1(act: Action, tmp_file_bi_in: Path, tmp_file_bi_out: Path, capsys):
    rows_to_add = 1000
    tmp_file_bi_in.write_text (f'''
    set bail on;
    set list on;

    -- do NOT use it !! >>> alter sequence g restart with 0; -- gen_id(g,1) will return 0 rather than 1 since 06-aug-2020 on FB 4.x !!

    delete from test;
    set term ^;
    execute block as
        declare c bigint;
    begin
        c = gen_id(g, -gen_id(g, 0)); -- restart sequence
    end
    ^
    set term ;^
    commit;

    set transaction lock timeout 7; -- THIS LOCK TIMEOUT SERVES ONLY FOR DELAY, see below auton Tx start.

    select current_timestamp as bulk_insert_start from rdb$database;
    set term ^;
    execute block as
        declare i int;
    begin
        execute procedure sp_ins({rows_to_add});
        begin
            -- #########################################################
            -- #######################  D E L A Y  #####################
            -- #########################################################
            in autonomous transaction do
            insert into test( x ) values({rows_to_add}); -- this will cause delay because of duplicate in index
        when any do
            begin
                i  =  gen_id(g,1);
            end
        end
    end
    ^
    set term ;^
    commit;
    select current_timestamp as bulk_insert_finish from rdb$database;
''')

    tx_param = ['WAIT', 'NO WAIT', 'LOCK TIMEOUT 1']
    #
    i = 0
    #
    for tx_decl in tx_param:
        idx_name = tx_decl.replace(' ', '_')
        idx_expr = "'" + idx_name + "'|| s"

        sql_create_indx = f'''
        set bail on;
        set list on;
        set blob all;
        select
            iif( gen_id(g,0) > 0 and gen_id(g,0) < 1 + {rows_to_add},
                 'OK, IS RUNNING',
                 iif( gen_id(g,0) <=0,
                      'WRONG: not yet started, current gen_id='||gen_id(g,0),
                      'WRONG: already finished, rows_to_add='|| {rows_to_add} ||', current gen_id='||gen_id(g,0)
                    )
               ) as inserts_state,
            current_timestamp as create_indx_start
        from rdb$database;
        set autoddl off;
        commit;

        set echo on;
        set transaction {tx_decl};

        create index test_{idx_name} on test computed by({idx_expr});
        commit;
        set echo off;

        select
            iif(  gen_id(g,0) >= 1 + {rows_to_add},
                  'OK, FINISHED',
                  'SOMETHING WRONG: current gen_id=' || gen_id(g,0)||', rows_to_add='|| {rows_to_add}
               ) as inserts_state
        from rdb$database;

        set count on;
        select
            rdb$index_name
            ,coalesce(rdb$unique_flag,0) as rdb$unique_flag
            ,coalesce(rdb$index_inactive,0) as rdb$index_inactive
            ,rdb$expression_source as rdb_expr_blob
        from rdb$indices ri
        where ri.rdb$index_name = upper( 'test_{idx_name}' )
        ;
        set count off;
        set echo on;
        set plan on;
        select 1 from test where {idx_expr} > '' rows 0;
        set plan off;
        set echo off;
        commit;
        drop index test_{idx_name};
        commit;
'''
        with open(tmp_file_bi_out, mode='w') as f_bulk_insert_log:
            # This will insert rows and then stay in pause 10 seconds:
            p_bulk_insert = subprocess.Popen([act.vars['isql'], act.db.dsn,
                                              '-user', act.db.user,
                                              '-password', act.db.password,
                                              '-q', '-i', str(tmp_file_bi_in)],
                                              stdout = f_bulk_insert_log,
                                              stderr = subprocess.STDOUT
                                              )
            #act.isql(switches=['-q'], input=sql_bulk_insert)
            #bulk_insert_log = act.stdout
            # 3.0 Classic: seems that it requires at least 2 seconds for ISQL be loaded into memory.
            time.sleep(3)
            # This will wait until first ISQL finished
            act.expected_stderr = 'DISABLED'
            act.isql(switches=['-q', '-n'], input=sql_create_indx)
            time.sleep(7) # NB: this delay plus previous (3+5=8) must be GREATER than lock timeout in <sql_bulk_insert>

            p_bulk_insert.terminate()
        bulk_insert_log = tmp_file_bi_out.read_text()
        create_indx_log = act.stdout + act.stderr

        log = act.string_strip(bulk_insert_log, act.substitutions)
        for line in log.splitlines():
            if line.strip():
                print( str(i)+': BULK INSERTS LOG: '+line.strip().upper() )

        log = act.string_strip(create_indx_log, act.substitutions)
        for line in log.splitlines():
            if line.strip():
                print( str(i)+': CREATE INDEX LOG: '+line.strip().upper() )
        #
        i += 1
    # Checks
    act.reset()
    act.stdout = capsys.readouterr().out
    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
