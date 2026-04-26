#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7954
TITLE:       Shared metacache. Check ability to ADD several indices while concurrent DML activity exists.
DESCRIPTION:
    Test creates table with seven columns (f01 ... f07), initially without indices. Field 'f06' is not null.
    Attach #1 adds records to this table and further remains 'idle' (without commit).
    Attach #2 creates indices for columns f01 ... f07. Part of them are created explicitly (via 'CREATE INDEX' statement),
    others are created implicitly by engine for support of declarative constraints (UNIQUE / PRIMARY KEY / FOREIGN KEY).
    NOTE-1: column 'f06' must be declared as NOT null because it will server as PRIMARY KEY in temporary created constraint.
    NOTE-2: we do NOT complete these actions by commit in order to check proper work of shared metadata cache.
    Then we run queries which must show that all new (non-committed) indices are avaliable for attach #2 (see 'chk_sql_lst').
    All queries must contain 'Index Range Scan' or 'Index Full Scan' in appropriate explained plan.
    Finally, we drop (in attach #2) every created index and run rollback.

    Test verifies these actions withing following loops:
    =================
        for <tx_til> in (<transactions_TIL_list>):
            for <relation_type> in ('PERMANENT', 'GTT_PRESERVE_ROWS', 'GTT_DELETE_ROWS'):
                <test scenario>
    =================
    NB. Only three TIL can be checked: read committed record_version; read consistency; snapshot.
NOTES:
    [26.04.2026] pzotov
    Currently test FAILS on check of GTT which is created with 'ON COMMIT DELETE ROWS': no new indices will be used.
    Sent report to FB-team, 26.04.2026 15:37.

    Checked on 6.0.0.1914-67e1176.
"""
import time
import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, DatabaseError, FirebirdWarning

db = db_factory()
act = python_act('db')

#-----------------------------------------------------------
def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped
#-----------------------------------------------------------

@pytest.mark.version('>=6')
def test_1(act: Action, capsys):

    # NB. We must NOT use following TILs:
    # 1) Isolation.READ_COMMITTED_NO_RECORD_VERSION. Otherwise attempt to query rdb$indices raises:
    # deadlock
    # read conflicts with concurrent update
    # concurrent transaction number is 31
    # (335544336, 335545096, 335544878)
    #
    # 2) Isolation.SERIALIZABLE. Otherwise attempt to DROP index (even w/o commit) raises:
    # lock conflict on no wait transaction
    # Acquire lock for relation ("SYSTEM"."RDB$INDICES") failed
    # (335544345, 335544382)
    
    tx_isol_lst = [ 
                    Isolation.READ_COMMITTED_RECORD_VERSION,
                    Isolation.READ_COMMITTED_READ_CONSISTENCY,
                    Isolation.SNAPSHOT,
                  ]

    # temp 4debug:
    #tx_isol_lst= [ Isolation.SNAPSHOT, ]

    # K = relation type; V = (rel_type, rel_name, optional_ddl_suffix):
    tab_ddl_map = {
       'permanent' : (0, '',                 'test_permanent'.upper(), ''),
       'gtt_sessn' : (4, 'global temporary', 'gtt_ssn'.upper(), 'on commit preserve rows'),
       #'gtt_trans' : (5, 'global temporary', 'gtt_tra'.upper(), 'on commit delete rows'),
    }

   
    # for any isolation mode attempt to run DDL for table that is in use by another Tx must fail
    # with the same error message. We check all possible Tx isolation modes for that:
    for x_isol in tx_isol_lst:
    
        custom_tpb = tpb(isolation = x_isol, lock_timeout = 0)

        for tab_type, tab_opts in tab_ddl_map.items():

            tt_type, tt_pref, tt_name, tt_suff = tab_opts[:4]
            tab_type_ddl = f'recreate {tt_pref} table {tt_name}(f01 int, f02 int, f03 int, f04 int, f05 int, f06 int not null, f07 int) {tt_suff}'

            # K = index_name ; V = (is_index_COMPUTED, is_index_PARTIAL, index_DDL)
            
            idx_info_query = """
                select
                    rr.rdb$relation_type as rel_type
                   ,trim(ri.rdb$index_name) as idx_name
                   ,coalesce(upper(ri.rdb$expression_source), rs.rdb$field_name) as idx_key
                   ,coalesce(rc.rdb$constraint_type,'') constrt_type
                   ,coalesce(rdb$unique_flag,0) as is_unique
                   ,sign(octet_length(coalesce(rdb$expression_source,''))) is_computed
                   ,sign(octet_length(coalesce(rdb$condition_source,''))) is_partial
               from rdb$relations rr
               join rdb$indices ri using(rdb$relation_name)
               left join rdb$relation_constraints rc using(rdb$index_name)
               left join rdb$index_segments rs using(rdb$index_name)
               where rr.rdb$relation_name = ?
               order by idx_name
            """
            
            print('TIL:', x_isol.name)
            print(f'Check: {tab_type=} {tt_suff}')

            with act.db.connect() as con_dba:
                ###################################
                ###   c r e a t e    t a b l e  ###
                ###################################
                con_dba.execute_immediate(tab_type_ddl)
                con_dba.commit()

            with act.db.connect() as con1, act.db.connect() as con2:
                tx1 = con1.transaction_manager(custom_tpb)
                tx2 = con2.transaction_manager(custom_tpb)
                tx1.begin()
                tx2.begin()
                with tx1.cursor() as cur1, tx2.cursor() as cur2:
                    try:
                        # DML 'insert into ... select from ...'. Index must be involved:
                        msg = 'att-1, point-1'
                        cur1.execute(f'insert into {tt_name}(f01, f02, f03, f04, f05, f06, f07) select i, i, i, i, i, i, null from generate_series(1, 1000) as s(i)')
                        cur1.execute(f"select count(*) from {tt_name} where f01 between ? and ?", (1, 11))

                        # Print explained plan with padding each line by dots in order to see indentations:
                        print(msg)
                        print( '\n'.join([replace_leading(s) for s in cur1.statement.detailed_plan.split('\n')]) )
                        
                        cur2.execute(f'insert into {tt_name}(f01, f02, f03, f04, f05, f06, f07) select -i, -i, -i, -i, -i, -i, -i from generate_series(1001, 2000) as s(i)')
                        
                        cur2.execute(f'create descending index {tt_name}_f01_regular_desc on {tt_name}(f01)')
                        cur2.execute(f'create unique index {tt_name}_f02_regular on {tt_name}(f02)')
                        cur2.execute(f'create index {tt_name}_f03_computed on {tt_name} computed by (f03)')
                        cur2.execute(f'create index {tt_name}_f04_partial on {tt_name} (f04) where f04 is not null')
                        cur2.execute(f'alter table {tt_name} add constraint {tt_name}_f05_unique unique(f05)')
                        cur2.execute(f'alter table {tt_name} add constraint {tt_name}_f06_pkey primary key(f06)')
                        cur2.execute(f'alter table {tt_name} add constraint {tt_name}_f07_fkey foreign key(f07) references {tt_name}(f06)')

                        chk_sql_lst = (
                            f'select max(f01) from {tt_name} where f01 < ?',
                            f'select count(*) from {tt_name} where f02 = ?',
                            f'select count(*) from {tt_name} where f03 = ?',
                            f'select count(*) from {tt_name} where f04 is not null',
                            f'select count(*) from {tt_name} where f05 = ?',
                            f'select count(*) from {tt_name} where f06 = ?',
                            f'select count(*) from {tt_name} where f07 = ?',
                        )
                        for i,chk_sql_stm in enumerate(chk_sql_lst):
                            msg = f'att-2, point-{i}'
                            print(msg)
                            ps = cur2.prepare(chk_sql_stm)
                            print(chk_sql_stm)
                            print( '\n'.join([replace_leading(x) for x in ps.detailed_plan.split('\n')]) )
                            ps.free()

                        cur2.execute(idx_info_query, (tt_name.upper().strip(),))
                        cur_cols = cur2.description
                        for r in cur2:
                            for i in range(0,len(cur_cols)):
                                print( cur_cols[i][0].ljust(32), ':', r[i] )

                        cur2.execute(f'drop index {tt_name}_f01_regular_desc')
                        cur2.execute(f'drop index {tt_name}_f02_regular')
                        cur2.execute(f'drop index {tt_name}_f03_computed')
                        cur2.execute(f'drop index {tt_name}_f04_partial')
                        cur2.execute(f'alter table {tt_name} drop constraint {tt_name}_f05_unique')
                        cur2.execute(f'alter table {tt_name} drop constraint {tt_name}_f07_fkey')
                        cur2.execute(f'alter table {tt_name} drop constraint {tt_name}_f06_pkey')

                        tx2.rollback()

                        cur2.execute(idx_info_query, (tt_name.upper().strip(),))
                        for r in cur2:
                            print('UNEXPECTED RECORDS:')
                            for i in range(0,len(cur_cols)):
                                print( cur_cols[i][0].ljust(32), ':', r[i] )

                        tx1.rollback()

                    except Exception as e:
                        print(e.__str__())
                        print(e.gds_codes)
                # < with tx1.cursor() as cur1, tx2.cursor() as cur2
            # < with act.db.connect() as con1, act.db.connect() as con2

            with act.db.connect() as con_dba:
                ################################
                ###   d r o p     t a b l e  ###
                ################################
                con_dba.execute_immediate(f'drop table {tt_name}')
                con_dba.commit()
        
            expected_out = f"""
                TIL: {x_isol.name}
                Check: {tab_type=} {tt_suff}
                att-1, point-1
                Select Expression
                ....-> Aggregate
                ........-> Filter
                ............-> Table "PUBLIC"."{tt_name}" Full Scan
                att-2, point-0
                select max(f01) from {tt_name} where f01 < ?
                Select Expression
                ....-> Aggregate
                ........-> Filter
                ............-> Table "PUBLIC"."{tt_name}" Access By ID
                ................-> Index "PUBLIC"."{tt_name}_F01_REGULAR_DESC" Range Scan (lower bound: 1/1)
                att-2, point-1
                select count(*) from {tt_name} where f02 = ?
                Select Expression
                ....-> Aggregate
                ........-> Filter
                ............-> Table "PUBLIC"."{tt_name}" Access By ID
                ................-> Bitmap
                ....................-> Index "PUBLIC"."{tt_name}_F02_REGULAR" Unique Scan
                att-2, point-2
                select count(*) from {tt_name} where f03 = ?
                Select Expression
                ....-> Aggregate
                ........-> Filter
                ............-> Table "PUBLIC"."{tt_name}" Access By ID
                ................-> Bitmap
                ....................-> Index "PUBLIC"."{tt_name}_F03_COMPUTED" Range Scan (full match)
                att-2, point-3
                select count(*) from {tt_name} where f04 is not null
                Select Expression
                ....-> Aggregate
                ........-> Filter
                ............-> Table "PUBLIC"."{tt_name}" Access By ID
                ................-> Bitmap
                ....................-> Index "PUBLIC"."{tt_name}_F04_PARTIAL" Full Scan
                att-2, point-4
                select count(*) from {tt_name} where f05 = ?
                Select Expression
                ....-> Aggregate
                ........-> Filter
                ............-> Table "PUBLIC"."{tt_name}" Access By ID
                ................-> Bitmap
                ....................-> Index "PUBLIC"."{tt_name}_F05_UNIQUE" Unique Scan
                att-2, point-5
                select count(*) from {tt_name} where f06 = ?
                Select Expression
                ....-> Aggregate
                ........-> Filter
                ............-> Table "PUBLIC"."{tt_name}" Access By ID
                ................-> Bitmap
                ....................-> Index "PUBLIC"."{tt_name}_F06_PKEY" Unique Scan
                att-2, point-6
                select count(*) from {tt_name} where f07 = ?
                Select Expression
                ....-> Aggregate
                ........-> Filter
                ............-> Table "PUBLIC"."{tt_name}" Access By ID
                ................-> Bitmap
                ....................-> Index "PUBLIC"."{tt_name}_F07_FKEY" Range Scan (full match)
                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F01_REGULAR_DESC
                IDX_KEY                          : F01
                CONSTRT_TYPE                     :
                IS_UNIQUE                        : 0
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0
                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F02_REGULAR
                IDX_KEY                          : F02
                CONSTRT_TYPE                     :
                IS_UNIQUE                        : 1
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0
                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F03_COMPUTED
                IDX_KEY                          : (F03)
                CONSTRT_TYPE                     :
                IS_UNIQUE                        : 0
                IS_COMPUTED                      : 1
                IS_PARTIAL                       : 0
                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F04_PARTIAL
                IDX_KEY                          : F04
                CONSTRT_TYPE                     :
                IS_UNIQUE                        : 0
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 1
                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F05_UNIQUE
                IDX_KEY                          : F05
                CONSTRT_TYPE                     : UNIQUE
                IS_UNIQUE                        : 1
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0
                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F06_PKEY
                IDX_KEY                          : F06
                CONSTRT_TYPE                     : PRIMARY KEY
                IS_UNIQUE                        : 1
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0
                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F07_FKEY
                IDX_KEY                          : F07
                CONSTRT_TYPE                     : FOREIGN KEY
                IS_UNIQUE                        : 0
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0
            """

            act.expected_stdout = expected_out
            act.stdout = capsys.readouterr().out
            assert act.clean_stdout == act.clean_expected_stdout
            act.reset()

