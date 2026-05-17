#coding:utf-8
"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/8b4893b3bdd3bd5e8dcc6b9953d3379dd196d268
TITLE:       Shared metacache. DROP <UNIQ_CONSTR> while concurrent Tx involving appropriate index; verify RDB$ content for such intermediate state.
DESCRIPTION:
    Test verifies ability to DROP UNIQUE constraint while its index is involved in work during DML actions perfoming by concurrent attachment.
    Main scenario works withing following loops:
    =================
        for <tx_til> in (<transactions_TIL_list>):
            for <relation_type> in ('PERMANENT', 'GTT_PRESERVE_ROWS', 'GTT_DELETE_ROWS'):
                <main scenario>
    =================
    NB-1 Only three TIL can be checked: read committed record_version; read consistency; snapshot.
    The <main scenario> run initial DDL and creates two attachments:
        * initial DDL: table with TWO unique constraints (one of them applies to single column (x), second - compound for columns (y,x) );
        * att-1 (initial point) runs some query (hereafter <Q>) that involves BOTH unique constrains (i.e. shows them both in explained plan);
        * att-2 drops 1st constraint but does NOT issue 'commit'; since that point 1st constraint must NOT be seen in RDB$ tables for current attach;
        * att-1 must still see same TWO indices in explained plan for the query <Q>;
        * att-2 runs <Q> and now it must only ONE index in the explained plan;
        * att-2 checks RDB$ tables (see func 'show_idx_info') for unique constraint that was just dropped (but Tx not yet committed):
          ** rdb$indices.rdb$index_name must have temporary name like 'RDB$TEMP_DEPEND_{test_table_id}_<n>'
          ** rdb$indices.rdb$index_inactive must have value 4;
          ** rdb$relation_constraints.rdb$constraint_type be NULL.
        * att-2 issues 'ROLLBACK'; since that point visibility of 1st constraint is 'restored' (it MUST be seen in RDB$ tables for current attach);
        * att-2 runs <Q> and now it must see BOTH indices in the explained plan;
    NB-2.
        We use substitutions in order to ignore details related to execution plan and access paths (Unique or Range Scans, names of indices).
        Only presense of one or two indices is checked in each case of execution plan.
NOTES:
    [17.05.2026] pzotov
    Original report to FB-team: 25.04.2026 1245.
    (subj: "alter table drop constraint <UNIQUE_CONSTR> does not change index name in rdb$indices to 'RDB$TEMP_DEPEND_...'")
    On Classic execution time is ~21 s (vs ~6.3 s on SS).
    Confirmed problem on 6.0.0.1942-7589a56.
    Checked on 6.0.0.1947-bbf461b.
"""
import time
import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, DatabaseError

db = db_factory()

substitutions = [
    ('Index ("PUBLIC".)?"TEST_UNIQUE_\\S+"', 'Index TEST_UNIQUE_***'),
    ('(Unique|Range) Scan.*', '<scan_op>')
]


act = python_act('db', substitutions = substitutions)

#-----------------------------------------------------------
def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped
#-----------------------------------------------------------

def show_idx_info(cur, tt_name, addi_msg = ''):

    print(addi_msg)
    idx_info_query = f"""
        select
            -- '{addi_msg}' as msg
            rr.rdb$relation_name as rel_name
           ,trim(ri.rdb$index_name) as idx_name
           ,coalesce(rdb$index_inactive,0) as is_inactive
           ,coalesce(rdb$unique_flag,0) as is_unique
           ,iif(trim(rc.rdb$constraint_type) = '', '[EMPTY STR]', trim(rc.rdb$constraint_type)) constr_type
        from rdb$relations rr
        left join rdb$indices ri using(rdb$relation_name)
        left join rdb$relation_constraints rc using(rdb$index_name)
        where rr.rdb$relation_name = ?
        order by rel_name, idx_name
        ;
    """
    
    cur.execute(idx_info_query, (tt_name.upper().strip(),))
    cur_cols = cur.description
    for r in cur:
        for i in range(0,len(cur_cols)):
            print( cur_cols[i][0].ljust(32), ':', '[NULL]' if r[i] == None else r[i] )


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
       'permanent' : (0, '',                 'test'.upper(), ''),
       'gtt_trans' : (5, 'global temporary', 'test'.upper(), 'on commit delete rows'),
       'gtt_sessn' : (4, 'global temporary', 'test'.upper(), 'on commit preserve rows'),
    }

    
    # for any isolation mode attempt to run DDL for table that is in use by another Tx must fail
    # with the same error message. We check all possible Tx isolation modes for that:
    for x_isol in tx_isol_lst:
    
        custom_tpb = tpb(isolation = x_isol, lock_timeout = 0)

        for tab_type, tab_opts in tab_ddl_map.items():

            tt_type, tt_pref, tt_name, tt_suff = tab_opts[:4]
            tab_type_ddl = f'recreate {tt_pref} table {tt_name}(x int, y int) {tt_suff}'

            idx_ddl_map = {}
            for k,v in { 'unique_singular' : '(x)', 'unique_compound' : '(y,x)' }.items():
                unq_constr_name = tt_name + '_' + k.upper()
                idx_ddl_map[ k.upper() ] = (unq_constr_name, f'alter table {tt_name} add constraint {unq_constr_name} unique {v}')
            
            with act.db.connect() as con_dba:
                ###################################
                ###   c r e a t e    t a b l e  ###
                ###################################
                con_dba.execute_immediate(tab_type_ddl)
                con_dba.commit()
                for idx_name, unq_constr_data in idx_ddl_map.items():
                    ####################################################
                    ###   c r e a t e    u n i q u e    c o n s t r. ###
                    ####################################################
                    con_dba.execute_immediate(unq_constr_data[1])
                    con_dba.commit()

            print('TIL:', x_isol.name)
            print(f'Check {tab_type=} {tt_suff}')
            test_table_id = -1
            for idx_name, unq_constr_data in idx_ddl_map.items():
                unq_constr_name, unq_ddl_expr = unq_constr_data[:3]

                print(f"Check drop/rollback {unq_constr_name=}")
                with act.db.connect() as con1, act.db.connect() as con2:
                    tx1 = con1.transaction_manager(custom_tpb)
                    tx2 = con2.transaction_manager(custom_tpb)
                    tx1.begin()
                    tx2.begin()
                    with tx1.cursor() as cur1, tx2.cursor() as cur2:
                        try:
                            msg = 'att-1, point-1: both indices must present in the execution plan'
                            get_rel_idx_id_sql = """
                                select rr.rdb$relation_id
                                from rdb$relations rr
                                where rr.rdb$relation_name = ?
                            """
                            cur1.execute(get_rel_idx_id_sql, (tt_name,))
                            for r in cur1:
                                test_table_id = r[0]
                            
                            assert test_table_id > 0

                            cur1.execute(f'insert into {tt_name}(x, y) select n, n from generate_series(1, 300) as s(n)')
                            
                            test_sql = f"""
                                select count(*) /* %s */
                                from (select x from {tt_name} where x between ? and ?) a
                                join (select y from {tt_name} where y between ? and ?) b
                                on a.x = b.y
                            """
                            cur1.execute(test_sql % msg, (7, 13, 12, 8))

                            # Print explained plan with padding eash line by dots in order to see indentations:
                            print(msg)
                            #print( '\n'.join([replace_leading(s) for s in cur1.statement.detailed_plan.split('\n')]) )
                            print( '\n'.join([ s for s in cur1.statement.detailed_plan.split('\n') if '-> Index ' in s ] ) )

                            cur2.execute(f'insert into {tt_name}(x, y) select -n, -n from generate_series(1, 100) as s(n)')

                            ############################################
                            ###   d r o p    u n i q    c o n s t r. ###
                            ############################################
                            msg = f'att-2, point-1: temporary dropped {unq_constr_name}'
                            print(msg)
                            cur2.execute(f'alter table {tt_name} /* {msg} */  drop constraint {unq_constr_name}')
                            #show_idx_info(cur2, tt_name, msg)
                            # <<< !DO NOT COMMIT! >>>

                            # +++++++++++++++++++++++++++++ [ 1 ] +++++++++++++++++++++++++++++

                            # Index {idx_name} must be still involved for ATT-1:
                            msg = 'att-1, point-2: both indices must present in the execution plan'
                            cur1.execute(test_sql % msg, (19, 61, 23, 47))
                            print(msg)
                            #print( '\n'.join([replace_leading(s) for s in cur1.statement.detailed_plan.split('\n')]) )
                            print( '\n'.join([ s for s in cur1.statement.detailed_plan.split('\n') if '-> Index ' in s ] ) )
                            for r in cur1:
                                pass

                            # +++++++++++++++++++++++++++++ [ 2 ] +++++++++++++++++++++++++++++
                            msg = 'att-2, point-2: temporary droppped constraint must have no name'
                            show_idx_info(cur2, tt_name, msg)
                            
                            ##########
                            # Only ONE of indices must be avaliable now for ATT-2:
                            ##########
                            msg = 'att-2, point-3: only one index must be used'
                            cur2.execute(test_sql % msg, (-18, -3, -17, -11))

                            print(msg)
                            #print( '\n'.join([replace_leading(s) for s in cur2.statement.detailed_plan.split('\n')]) )
                            print( '\n'.join([ s for s in cur2.statement.detailed_plan.split('\n') if '-> Index ' in s ] ) )
                            for r in cur2:
                                pass

                            ###################################################
                            ###  r o l b a c k     d r o p     c o n s t r. ###
                            ###################################################
                            tx2.rollback() # <<< this must allow ATT-2 again to use index! But this att must add records again.
                            # +++++++++++++++++++++++++++++ [ 3 ] +++++++++++++++++++++++++++++
                            tx2.begin()

                            msg = f'att-2, point-4: constraint restored, its original name "{unq_constr_name}" must be shown'
                            show_idx_info(cur2, tt_name, msg)
                            
                            # Both indices must be again avaliable now for ATT-2:
                            msg = 'att-2, point-5: both indices AGAIN must present in the execution plan'
                            cur2.execute(test_sql % msg, (-19, -9, -17, -13))

                            print(msg)
                            #print( '\n'.join([replace_leading(s) for s in cur2.statement.detailed_plan.split('\n')]) )
                            print( '\n'.join([ s for s in cur2.statement.detailed_plan.split('\n') if '-> Index ' in s ] ) )
                            for r in cur2:
                                pass

                            tx1.rollback()
                            # tx2.rollback()

                        except DatabaseError as e:
                            print(e.__str__())
                            print(e.gds_codes)
                    # < with tx1.cursor() as cur1, tx2.cursor() as cur2
                # < with act.db.connect() as con1, act.db.connect() as con2

                #with act.db.connect() as con_dba:
                #    con_dba.execute_immediate(f'alter table {tt_name} drop constraint {unq_constr_name}')
                #    con_dba.commit()
            # < for idx_name, unq_constr_data in idx_ddl_map

            expected_out = f"""
                TIL: {x_isol.name}
                Check {tab_type=} {tt_suff}

                Check drop/rollback unq_constr_name='TEST_UNIQUE_SINGULAR'
                
                att-1, point-1: both indices must present in the execution plan
                -> Index TEST_UNIQUE_*** <scan_op>
                -> Index TEST_UNIQUE_*** <scan_op>

                att-2, point-1: temporary dropped TEST_UNIQUE_SINGULAR

                att-1, point-2: both indices must present in the execution plan
                -> Index TEST_UNIQUE_*** <scan_op>
                -> Index TEST_UNIQUE_*** <scan_op>

                att-2, point-2: temporary droppped constraint must have no name
                REL_NAME                         : {tt_name}
                IDX_NAME                         : RDB$TEMP_DEPEND_{test_table_id}_0
                IS_INACTIVE                      : 4
                IS_UNIQUE                        : 1
                CONSTR_TYPE                      : [NULL]
                REL_NAME                         : {tt_name}
                IDX_NAME                         : {tt_name}_{sorted(idx_ddl_map.keys())[0]}
                IS_INACTIVE                      : 0
                IS_UNIQUE                        : 1
                CONSTR_TYPE                      : UNIQUE

                att-2, point-3: only one index must be used
                -> Index TEST_UNIQUE_*** <scan_op>

                att-2, point-4: constraint restored, its original name "TEST_UNIQUE_SINGULAR" must be shown
                REL_NAME                         : {tt_name}
                IDX_NAME                         : {tt_name}_{sorted(idx_ddl_map.keys())[0]}
                IS_INACTIVE                      : 0
                IS_UNIQUE                        : 1
                CONSTR_TYPE                      : UNIQUE

                REL_NAME                         : {tt_name}
                IDX_NAME                         : {tt_name}_{sorted(idx_ddl_map.keys())[1]}
                IS_INACTIVE                      : 0
                IS_UNIQUE                        : 1
                CONSTR_TYPE                      : UNIQUE
                
                att-2, point-5: both indices AGAIN must present in the execution plan
                -> Index TEST_UNIQUE_*** <scan_op>
                -> Index TEST_UNIQUE_*** <scan_op>

                
                Check drop/rollback unq_constr_name='TEST_UNIQUE_COMPOUND'
                
                att-1, point-1: both indices must present in the execution plan
                -> Index TEST_UNIQUE_*** <scan_op>
                -> Index TEST_UNIQUE_*** <scan_op>

                att-2, point-1: temporary dropped TEST_UNIQUE_COMPOUND
                
                att-1, point-2: both indices must present in the execution plan
                -> Index TEST_UNIQUE_*** <scan_op>
                -> Index TEST_UNIQUE_*** <scan_op>

                att-2, point-2: temporary droppped constraint must have no name
                REL_NAME                         : {tt_name}
                IDX_NAME                         : RDB$TEMP_DEPEND_{test_table_id}_1
                IS_INACTIVE                      : 4
                IS_UNIQUE                        : 1
                CONSTR_TYPE                      : [NULL]
                REL_NAME                         : {tt_name}
                IDX_NAME                         : {tt_name}_{sorted(idx_ddl_map.keys())[1]}
                IS_INACTIVE                      : 0
                IS_UNIQUE                        : 1
                CONSTR_TYPE                      : UNIQUE
                
                att-2, point-3: only one index must be used
                -> Index TEST_UNIQUE_*** <scan_op>

                att-2, point-4: constraint restored, its original name "TEST_UNIQUE_COMPOUND" must be shown
                REL_NAME                         : {tt_name}
                IDX_NAME                         : {tt_name}_{sorted(idx_ddl_map.keys())[0]}
                IS_INACTIVE                      : 0
                IS_UNIQUE                        : 1
                CONSTR_TYPE                      : UNIQUE

                REL_NAME                         : {tt_name}
                IDX_NAME                         : {tt_name}_{sorted(idx_ddl_map.keys())[1]}
                IS_INACTIVE                      : 0
                IS_UNIQUE                        : 1
                CONSTR_TYPE                      : UNIQUE

                att-2, point-5: both indices AGAIN must present in the execution plan
                -> Index TEST_UNIQUE_*** <scan_op>
                -> Index TEST_UNIQUE_*** <scan_op>
            """

            act.expected_stdout = expected_out
            act.stdout = capsys.readouterr().out
            assert act.clean_stdout == act.clean_expected_stdout
            act.reset()
        # < for tab_type, tab_opts in tab_ddl_map.items
    # < for x_isol in tx_isol_lst
