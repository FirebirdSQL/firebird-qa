#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7954
TITLE:       Shared metacache. Check ability to ADD indices/constraints, run DML and DROP indices/constraints.
DESCRIPTION:
    Test verifies several DDL and DML statements withing following loops:
    =================
        for <tx_til> in (<transactions_TIL_list>):
            for <relation_type> in ('PERMANENT', 'GTT_PRESERVE_ROWS', 'GTT_DELETE_ROWS'):
                <test scenario>
    =================
    - where <test scenario> is set of following actions performed within SAME transaction:
        * create descending index;
        * create unique index;
        * create COMPUTED-BY index;
        * create PARTIAL index;
        * add UNIQUE constraint to the table;
        * add PRIMARY KEY constraint to the table;
        * add FOREIGN KEY constraint to the table;
        * add some number of rows to the table (values must satisfy UK/PK/FK requirements);
        * drop all indices which were created by 'CREATE INDEX' statement;
        * drop all CONSTRAINTS (unique; FK; PK).
    No errors must occur.
NOTES:
    [26.04.2026] pzotov
        Currently test FAILS on check of GTT which is created with 'ON COMMIT DELETE ROWS': no new indices will be used.
        Sent report to FB-team, 26.04.2026 15:37.
        Checked on 6.0.0.1914-67e1176.
    [21.06.2026] pzotov
        All kinds of TIL must pass (originally READ_COMMITTED_NO_RECORD_VERSION and SERIALIZABLE were skipped).
        Problems have been fixed in #fa5ffeba ("Fix for crash when table with index is recreated N times"), 15.06.2026 13:57.
        NOTE: commit #9c7090dd ("Fixed control on index dependencies when index to be deleted") was done in the same push as
        #fa5ffeba but it appears insufficient and bug still existed (test raised "cannot delete/TABLE .../there are 2 dependencies")

    Checked on 6.0.0.2009-fa5ffeb; 6.0.0.2022-3bca222.
"""
import time
import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, DatabaseError, FirebirdWarning

db = db_factory()
act = python_act('db')

RECORDS_COUNT = 1000

#-----------------------------------------------------------
def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped
#-----------------------------------------------------------

@pytest.mark.version('>=6')
def test_1(act: Action, capsys):
    
    tx_isol_lst = [ 
                    Isolation.READ_COMMITTED_RECORD_VERSION,
                    Isolation.READ_COMMITTED_READ_CONSISTENCY,
                    Isolation.SNAPSHOT,
                    Isolation.SERIALIZABLE,
                    Isolation.READ_COMMITTED_NO_RECORD_VERSION,
                  ]

    # K = relation type; V = (rel_type, rel_name, optional_ddl_suffix):
    tab_ddl_map = {
       'permanent' : (0, '',                 'test_permanent'.upper(), ''),
       'gtt_sessn' : (4, 'global temporary', 'gtt_ssn'.upper(), 'on commit preserve rows'),
       'gtt_trans' : (5, 'global temporary', 'gtt_tra'.upper(), 'on commit delete rows'),
    }

   
    # for any isolation mode attempt to run DDL for table that is in use by another Tx must fail
    # with the same error message. We check all possible Tx isolation modes for that:
    for x_isol in tx_isol_lst:
    
        custom_tpb = tpb(isolation = x_isol, lock_timeout = 0)

        for tab_type, tab_opts in tab_ddl_map.items():

            tt_type, tt_pref, tt_name, tt_suff = tab_opts[:4]
            tab_type_ddl = f'recreate {tt_pref} table {tt_name}(f01 varbinary(16) not null, f02 varbinary(16)) {tt_suff}'

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

            with act.db.connect() as con1:
                tx1 = con1.transaction_manager(custom_tpb)
                tx1.begin()
                with tx1.cursor() as cur1:
                    try:
                        # DML 'insert into ... select from ...'. Index must be involved:
                        msg = 'att-1, point-1'
                        cur1.execute(f'insert into {tt_name}(f01) select gen_uuid() from generate_series(1, {RECORDS_COUNT}) as s(i)')
                        tx1.commit()

                        tx1.begin()
                        cur1.execute(f'create descending index {tt_name}_f01_regular_desc on {tt_name}(f01)')
                        cur1.execute(f'create unique index {tt_name}_f01_regular on {tt_name}(f01)')
                        cur1.execute(f"create index {tt_name}_f01_computed on {tt_name} computed by (crypt_hash(f01 using sha1))")
                        cur1.execute(f'create index {tt_name}_f01_partial on {tt_name} (f01) where f01 is not null')
                        cur1.execute(f'alter table {tt_name} add constraint {tt_name}_f02_unique unique(f02)')
                        cur1.execute(f'alter table {tt_name} add constraint {tt_name}_f01_pkey primary key(f01)')
                        cur1.execute(f'alter table {tt_name} add constraint {tt_name}_f01_fkey foreign key(f01) references {tt_name}(f01)')

                        cur1.execute(f'insert into {tt_name}(f01, f02) select g,g from (select gen_uuid() g from generate_series(1, {RECORDS_COUNT}) as s(i))')

                        cur1.execute(idx_info_query, (tt_name.upper().strip(),))
                        cur_cols = cur1.description
                        for r in cur1:
                            for i in range(0,len(cur_cols)):
                                print( cur_cols[i][0].ljust(32), ':', r[i] )

                        cur1.execute(f'drop index {tt_name}_f01_regular_desc')
                        cur1.execute(f'drop index {tt_name}_f01_regular')
                        cur1.execute(f'drop index {tt_name}_f01_computed')
                        cur1.execute(f'drop index {tt_name}_f01_partial')
                        cur1.execute(f'alter table {tt_name} drop constraint {tt_name}_f02_unique')
                        cur1.execute(f'alter table {tt_name} drop constraint {tt_name}_f01_fkey')
                        cur1.execute(f'alter table {tt_name} drop constraint {tt_name}_f01_pkey')
                        tx1.commit()

                    except Exception as e:
                        print(e.__str__())
                        print(e.gds_codes)
                # < with tx1.cursor() as cur1
            # < with act.db.connect() as con1

            with act.db.connect() as con_dba:
                ################################
                ###   d r o p     t a b l e  ###
                ################################
                con_dba.execute_immediate(f'drop table {tt_name}')
                con_dba.commit()
        
            expected_out = f"""
                TIL: {x_isol.name}
                Check: {tab_type=} {tt_suff}
                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F01_COMPUTED
                IDX_KEY                          : (CRYPT_HASH(F01 USING SHA1))
                CONSTRT_TYPE                     :
                IS_UNIQUE                        : 0
                IS_COMPUTED                      : 1
                IS_PARTIAL                       : 0

                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F01_FKEY
                IDX_KEY                          : F01
                CONSTRT_TYPE                     : FOREIGN KEY
                IS_UNIQUE                        : 0
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0

                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F01_PARTIAL
                IDX_KEY                          : F01
                CONSTRT_TYPE                     :
                IS_UNIQUE                        : 0
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 1

                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F01_PKEY
                IDX_KEY                          : F01
                CONSTRT_TYPE                     : PRIMARY KEY
                IS_UNIQUE                        : 1
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0

                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F01_REGULAR
                IDX_KEY                          : F01
                CONSTRT_TYPE                     :
                IS_UNIQUE                        : 1
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0

                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F01_REGULAR_DESC
                IDX_KEY                          : F01
                CONSTRT_TYPE                     :
                IS_UNIQUE                        : 0
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0

                REL_TYPE                         : {tt_type}
                IDX_NAME                         : {tt_name}_F02_UNIQUE
                IDX_KEY                          : F02
                CONSTRT_TYPE                     : UNIQUE
                IS_UNIQUE                        : 1
                IS_COMPUTED                      : 0
                IS_PARTIAL                       : 0
            """

            act.expected_stdout = expected_out
            act.stdout = capsys.readouterr().out
            assert act.clean_stdout == act.clean_expected_stdout
            act.reset()

