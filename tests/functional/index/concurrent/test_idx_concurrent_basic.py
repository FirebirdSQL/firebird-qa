#coding:utf-8
"""
ID:          functional.index.concurrent.test_idx_concurrent_basic
TITLE:       
DESCRIPTION:
NOTES:
    [21.08.2026] pzotov
    Checked on
"""
import socket
import subprocess
import shutil
import locale
import time
import datetime as py_dt
from pathlib import Path
import pytest
from firebird.qa import *
from firebird.driver import tpb, TraAccessMode, Isolation, DatabaseError

##########################
###   S E T T I N G S  ###
##########################
MAX_WAIT_IDX_BUILD_START_MS = 20000

init_script = """
    recreate table taud(id int, delay_ms int);
    recreate table test(id int);
    create or alter view v_idx_info as
    select
        rdb$index_name as idx_name
        ,rdb$unique_flag as idx_uniq
        ,rdb$index_inactive as idx_inactive
        ,rdb$expression_source as idx_expr_blob_id
    from rdb$indices where rdb$index_name = upper('test_id_expr');
    commit;
"""
db = db_factory(init = init_script)

substitutions = [('[ \t]+', ' '), ('(-)?After line .*', ''), ('IDX_EXPR_BLOB_ID.*', 'IDX_EXPR_BLOB_ID')]
act = python_act('db', substitutions = substitutions)
tmp_sql = temp_file('tmp_idx.sql')
tmp_log = temp_file('tmp_idx.log')


#------------------------------------------------------------------------------------
# Registered Ports (1024 ... 49151): Assigned by the Internet Assigned Numbers Authority (IANA)
# to specific vendor programs like MySQL (3306) or PostgreSQL (5432)
def get_free_port_in_range(start_port, end_port, hostname = 'localhost'):
    """Finds and returns the first available free port within a specified range."""
    for port in range(start_port, end_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                # Set SO_REUSEADDR to avoid immediate "Address already in use" errors
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind((hostname, port))
                return port
            except socket.error:
                continue  # Port is in use, try the next one
                
    raise OSError(f"No free ports available in range {start_port}-{end_port}")
#------------------------------------------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, tmp_sql: Path, tmp_log: Path, capsys):

    unused_port = get_free_port_in_range(3051, 49151)
    INDEX_EXPR = f'iif(id >=0, id + 0 * fn_wasted_time({unused_port}, id), -1)'

    for mode in ('alter',):
    #for mode in ('create',):
        if mode == 'create':
           INIT_INDEX_DDL = f'create unique index test_id_expr on test computed by ( {INDEX_EXPR} ) CONCURRENTLY;'
           ALTER_INDEX_DDL = ''
        else:
           INIT_INDEX_DDL = f'create unique index test_id_expr INACTIVE on test computed by ( {INDEX_EXPR} );'
           ALTER_INDEX_DDL = f'alter index test_id_expr active CONCURRENTLY;'

        test_sql = f"""
            set bail on;
            set list on;
            set blob all;
            set autoddl off;
            set autoterm on;
            set keep_tran on;
            commit;
            create or alter function fn_wasted_time(a_unused_port int, a_id int) returns int as
                declare t timestamp;
                declare v_delay int;
            begin
                t = 'now';
                begin
                    execute statement ('select 1 from rdb$database')
                    on external 'localhost/' || a_unused_port || ':' || rdb$get_context('SYSTEM', 'DB_NAME')
                    as user '{act.db.user}' password '{act.db.password}'
                    into v_delay;
                when any do
                    begin
                        -- execution *must* fall here, it is expected:
                        v_delay = datediff(millisecond from t to cast('now' as timestamp));
                        in autonomous transaction do
                        begin
                            -- put signal to break from loop and start consurrent attachment
                            -- with inserting rows that will cause duplicated key
                            execute statement ('insert into taud(id, delay_ms) values(?, ?)') (:a_id, :v_delay);
                        end
                    end
                end
                return v_delay;
            end;
            {INIT_INDEX_DDL if mode == 'alter' else ''}
            commit;

            delete from taud;
            delete from test;
            insert into test(id) select i from generate_series(1,7) as s(i);
            commit;
            set bail OFF;
            {INIT_INDEX_DDL if mode == 'create' else ALTER_INDEX_DDL}
            commit;
            select * from v_idx_info;
            show index test_id_expr;
            set list off;
            select * from test;
            quit; -- temporary

            /*
            alter index test_id_expr validate unique;
            commit;
            select * from v_idx_info;
            commit;
            delete from test where id < 0;
            commit;
            alter index test_id_expr validate unique;
            commit;
            select * from v_idx_info;
            commit;
            drop index test_id_expr;
            commit;
            */
        """
        tmp_sql.write_text(test_sql)
        con_watched = None
        p_idx_maker = None
        with open(tmp_log, mode='w') as f:
            with act.db.connect() as con_monitoring:
                tpb_monitoring = tpb(isolation=Isolation.READ_COMMITTED_RECORD_VERSION, lock_timeout=0)
                #tpb_monitoring = tpb(isolation=Isolation.READ_COMMITTED_READ_CONSISTENCY, lock_timeout=0)
                tx_monitoring = con_monitoring.transaction_manager(tpb_monitoring)
                cur_monitoring = tx_monitoring.cursor()
                
                iter = 0
                t1=py_dt.datetime.now()
                while True:
                    if iter == 0:
                        ####################################
                        ###   c r e a t e    i n d e x   ###
                        ####################################
                        p_idx_maker = subprocess.Popen([act.vars['isql'], '-n', '-i', str(tmp_sql),
                                                       '-user', act.db.user,
                                                       '-password', act.db.password, act.db.dsn],
                                                       stdout = f, stderr = subprocess.STDOUT)

                    tx_monitoring.begin()

                    sql_watched = f"""
                        select /* trace_me: waiting for index building start, iter #{iter} */ a.mon$attachment_id
                        from mon$attachments a
                        where
                            mon$attachment_id != current_connection
                            and trim(lower(mon$remote_process)) similar to '%[\\/]isql(.exe)?'
                            and exists(select 1 from taud)
                    """
                    cur_monitoring.execute(sql_watched)
                    con_watched = cur_monitoring.fetchone()
                    tx_monitoring.rollback()
                    #tx_monitoring.commit()
                    if con_watched:
                        break
                    else:
                        t2=py_dt.datetime.now()
                        d1=t2-t1
                        if d1.seconds*1000 + d1.microseconds//1000 >= MAX_WAIT_IDX_BUILD_START_MS:
                            break
                        else:
                            time.sleep(0.2)

                    iter += 1

                if con_watched and p_idx_maker:
                    assert p_idx_maker.poll() is None, f"\nISQL process which had to run valuable time completed too fast."

                    tx_monitoring.begin()
                    cur_monitoring.execute(f'insert /* trace_me: must occur BEFORE index building finished in ATT_{con_watched[0]} */ into test(id) select -123 from generate_series(1,3) as s(i)')
                    tx_monitoring.commit()

                    p_idx_maker.wait()

            # < with act.db.connect() as con_monitoring

        # < with open(tmp_log, mode='w')

        print(tmp_log.read_text())
        shutil.copy2(act.db.db_path, r'c:\temp\tmp4test.fdb')

        act.expected_stdout = f"""
            Uniqueness validation of the index "PUBLIC"."TEST_ID_EXPR" failed
            -attempt to store duplicate value (visible to active transactions) in unique index "PUBLIC"."TEST_ID_EXPR"
            -Problematic key value is (<expression> = -1)

            Statement failed, SQLSTATE = 23000
            unsuccessful metadata update
            -ALTER INDEX "PUBLIC"."TEST_ID_EXPR" failed
            -Uniqueness validation of the index "PUBLIC"."TEST_ID_EXPR" failed
            -attempt to store duplicate value (visible to active transactions) in unique index "PUBLIC"."TEST_ID_EXPR"
            -Problematic key value is (<expression> = -1)

            IDX_NAME TEST_ID_EXPR
            IDX_UNIQ 3
            IDX_INACTIVE 0
            IDX_EXPR_BLOB_ID
            ( {INDEX_EXPR} )

            IDX_NAME TEST_ID_EXPR
            IDX_UNIQ 1
            IDX_INACTIVE 0
            IDX_EXPR_BLOB_ID
            ( {INDEX_EXPR} )

        """
        act.expected_stdout = f"""
        """
        act.stdout = capsys.readouterr().out
        assert act.clean_stdout == act.clean_expected_stdout
