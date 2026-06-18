#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/fa5ffeba354b7aa5b505c1d4e367028e119472a2
TITLE:       Shared metacache. Fixed control on index dependencies when index to be deleted. Fix for crash when table with index is recreated N times
DESCRIPTION:
    Test verifies ability to DROP index after its creation and involving in a trivial query.
    Also values of natural and indexed reads are verified when index is just created.
    Main scenario works withing following loops:
    =================
        for <tx_til> in (<transactions_TIL_list>):
            for <relation_type> in ('PERMANENT', 'GTT_PRESERVE_ROWS', 'GTT_DELETE_ROWS'):
                for <index_type> in ('REGULAR', 'COMPUTED_BY', 'PARTIAL'):
                    <main scenario>
    =================
    NB. Only three TIL can be checked: read committed record_version; read consistency; snapshot.
NOTES:
    [18.06.2026] pzotov
    Test initially was made for check commit #c62f0609 ("Fixed DROP INDEX on temporary per-transaction table")
    but it appeared to be insufficient for problem fix.
    Discussion: https://groups.google.com/g/firebird-devel/c/avJi2t-0Av4/m/c47RE7KxAQAJ
    Bug fixed on #fa5ffeba ("Fix for crash when table with index is recreated N times"), 15.06.2026 13:57.
    Checked on 6.0.0.2009-fa5ffeba.
"""

import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, DatabaseError, FirebirdWarning

ROWS_TO_ADD = 1000

db = db_factory()
substitutions = [ ('[ \t]+', ' '), (r'RDB\$TEMP_DEPEND_\d+.*', 'RDB_TEMP_DEPEND') ]
act = python_act('db', substitutions = substitutions)

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

    # K = relation type; V = (rel_type, rel_name, optional_ddl_suffix):
    tab_ddl_map = {
        'permanent' : (0, '',                 'permanent_test'.upper(), '')
       ,'gtt_trans' : (5, 'global temporary', 'gtt_trn_test'.upper(), 'on commit delete rows')
       ,'gtt_sessn' : (4, 'global temporary', 'gtt_att_test'.upper(), 'on commit preserve rows')
    }

    get_rel_id = """
        select rr.rdb$relation_id
        from rdb$relations rr
        where rr.rdb$relation_name = ?
    """
    
    # for any isolation mode attempt to run DDL for table that is in use by another Tx must fail
    # with the same error message. We check all possible Tx isolation modes for that:
    for x_isol in tx_isol_lst:
    
        custom_tpb = tpb(isolation = x_isol, lock_timeout = 0)

        for tab_type, tab_opts in tab_ddl_map.items():

            tt_type, tt_pref, tt_name, tt_suff = tab_opts[:4]
            tab_type_ddl = f'recreate {tt_pref} table {tt_name}(x int) {tt_suff}'

            # K = index_name ; V = (is_index_COMPUTED, is_index_PARTIAL, index_DDL)
            idx_ddl_map = {
                'idx_regular'.upper()  : ( 0, 0, f'create index idx_regular on {tt_name}(x)' )
               ,'idx_computed'.upper() : ( 1, 0, f'create index idx_computed on {tt_name} computed by(x)' )
               ,'idx_partial'.upper()  : ( 0, 1, f'create index idx_partial on {tt_name}(x) where x is not null' )
            }

            idx_info_query = """
                select
                    rr.rdb$relation_type as rel_type
                   ,trim(ri.rdb$index_name) as idx_name
                   ,ri.rdb$index_inactive as idx_inactive
                   ,sign(octet_length(coalesce(ri.rdb$expression_source,''))) is_computed
                   ,sign(octet_length(coalesce(ri.rdb$condition_source,''))) is_partial
               from rdb$relations rr
               left join rdb$indices ri using(rdb$relation_name)
               where rr.rdb$relation_name = ?
               order by 1
            """
            
            for idx_name, idx_opts in idx_ddl_map.items():

                print('TIL:', x_isol.name)
                print(f'Check {tab_type=} {tt_suff}')

                idx_computed, idx_partial, idx_ddl = idx_opts[:3]
                test_table_id = -1
                with act.db.connect() as con:
                    tx1 = con.transaction_manager(custom_tpb)
                    cur = tx1.cursor()

                    try:
                        ###################################
                        ###   c r e a t e    t a b l e  ###
                        ###################################
                        cur.execute(tab_type_ddl)

                        cur.execute( "select rdb$relation_id from rdb$relations where rdb$relation_name = ?", (tt_name.upper(),) )
                        test_rel_id = None
                        for r in cur:
                            test_rel_id = r[0]
                        assert test_rel_id


                        ##################################
                        ###   i n s e r t    d a t a   ###
                        ##################################
                        cur.execute(f'insert into {tt_name}(x) select i from generate_series(1, {ROWS_TO_ADD}) as s(i)')

                        ###################################
                        ###   c r e a t e    i n d e x  ###
                        ###################################
                        cur.execute(idx_ddl)

                        ######################################################
                        ###   c h e c k    i n d e x    i n v o l v i n g  ###
                        ######################################################
                        cur.execute(f'select count(*) from {tt_name} where x = ?', (ROWS_TO_ADD//2,))
                        tabstat1 = [ p for p in con.info.get_table_access_stats() if p.table_id == test_rel_id ]
                        cur.fetchone()
                        tabstat2 = [ p for p in con.info.get_table_access_stats() if p.table_id == test_rel_id ]
                        
                        nat_reads = (tabstat2[0].sequential if tabstat2[0].sequential else 0) - (tabstat1[0].sequential if tabstat1[0].sequential else 0)
                        idx_reads = (tabstat2[0].indexed if tabstat2[0].indexed else 0) - (tabstat1[0].indexed if tabstat1[0].indexed else 0)

                        assert nat_reads == 0 and idx_reads == 1, f'INDEX DDL: {idx_ddl} - unexpected count of {nat_reads=} and/or {idx_reads=}.'

                        ###############################
                        ###   d r o p    i n d e x  ###
                        ###############################
                        cur.execute(f'drop index {idx_name}')
                        
                        ############################################
                        ###   c h e c k    r d b    t a b l e s  ###
                        ############################################
                        cur.execute(idx_info_query, (tt_name.upper().strip(),))
                        cur_cols = cur.description
                        for r in cur:
                            for i in range(0,len(cur_cols)):
                                print( cur_cols[i][0].ljust(32), ':', r[i] )
                        
                        tx1.commit()
                    except DatabaseError as e:
                        print(e.__str__())
                        print(e.gds_codes)

                expected_out = f"""
                    TIL: {x_isol.name}
                    Check {tab_type=} {tt_suff}

                    REL_TYPE                         : {tt_type}
                    IDX_NAME                         : RDB_TEMP_DEPEND
                    IDX_INACTIVE                     : 4
                    IS_COMPUTED                      : {idx_computed}
                    IS_PARTIAL                       : {idx_partial}
                """
                # IDX_NAME                         : RDB$TEMP_DEPEND_{test_table_id}_0

                act.expected_stdout = expected_out
                act.stdout = capsys.readouterr().out
                assert act.clean_stdout == act.clean_expected_stdout
                act.reset()
            # < for idx_name, idx_opts in idx_ddl_map.items()
