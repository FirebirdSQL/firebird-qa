#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7954
TITLE:       Shared metacache. Check ability to DROP INDEX <X> while concurrent DML activity exists that involves index <X>
DESCRIPTION:
    Test verifies ability to DROP index while it is involved in work during DML actions perfoming by concurrent attachment.
    Main scenario works withing following loops:
    =================
        for <tx_til> in (<transactions_TIL_list>):
            for <relation_type> in ('PERMANENT', 'GTT_PRESERVE_ROWS', 'GTT_DELETE_ROWS'):
                for <index_type> in ('REGULAR', 'COMPUTED_BY', 'PARTIAL'):
                    <main scenario>
    =================
    NB. Only three TIL can be checked: read committed record_version; read consistency; snapshot.
    The <main scenario> is:
        * att-1: runs DML like 'insert into <T>(<X>) select from ...' where <T.X> is indexed column. NO commit is done here;
        * att-2: tries to DROP INDEX for T.X column (this must pass). NO commit is done here;
        * att-1: runs 'select ... from test where x between ? and ?'; explained plan must show INDEXED range scan;
        * att-2: runs the same query; explained plan must show NATURAL access (i.e. table full scan);
        * att-1: rollbacks statement 'DROP INDEX ...' and runs query to T.X; plan must show again ("reverted") INDEXED scan.
NOTES:
    [23.04.2026] pzotov
    Test duiration time: ~15 sec.
    Checked on 6.0.0.1914-67e1176.
"""

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
        'permanent' : (0, '',                 'test'.upper(), '')
       ,'gtt_trans' : (5, 'global temporary', 'test'.upper(), 'on commit delete rows')
       ,'gtt_sessn' : (4, 'global temporary', 'test'.upper(), 'on commit preserve rows')
    }

    
    # for any isolation mode attempt to run DDL for table that is in use by another Tx must fail
    # with the same error message. We check all possible Tx isolation modes for that:
    for x_isol in tx_isol_lst:
    
        custom_tpb = tpb(isolation = x_isol, lock_timeout = 0)

        for tab_type, tab_opts in tab_ddl_map.items():

            tt_type, tt_pref, tt_name, tt_suff = tab_opts[:4]
            tab_type_ddl = f'recreate {tt_pref} table {tt_name}(x int, y int) {tt_suff}'

            # K = index_name ; V = (is_index_COMPUTED, is_index_PARTIAL, index_DDL)
            idx_ddl_map = {
                'idx_regular'.upper()     : ( 0, 0, f'create index idx_regular on {tt_name}(x)' )
               ,'idx_computed'.upper()    : ( 1, 0, f'create index idx_computed on {tt_name} computed by(x)' )
               ,'idx_partial'.upper() : ( 0, 1, f'create index idx_partial on {tt_name}(x) where x is not null' )
            }

            idx_info_query = """
                select
                    rr.rdb$relation_type as rel_type
                   ,trim(ri.rdb$index_name) as idx_name
                   ,sign(octet_length(coalesce(rdb$expression_source,''))) is_computed
                   ,sign(octet_length(coalesce(rdb$condition_source,''))) is_partial
               from rdb$relations rr left join rdb$indices ri using(rdb$relation_name)
               where rr.rdb$relation_name = ?
               order by 1
            """
            
            for idx_name, idx_opts in idx_ddl_map.items():

                print('TIL:', x_isol.name)
                print(f'Check {tab_type=} {tt_suff}')

                idx_computed, idx_partial, idx_ddl = idx_opts[:3]

                with act.db.connect() as con_dba:
                    ###################################
                    ###   c r e a t e    t a b l e  ###
                    ###################################
                    con_dba.execute_immediate(tab_type_ddl)
                    con_dba.commit()

                    ###################################
                    ###   c r e a t e    i n d e x  ###
                    ###################################
                    con_dba.execute_immediate(idx_ddl)
                    con_dba.commit()

                    cur = con_dba.cursor()
                    cur.execute(idx_info_query, (tt_name.upper().strip(),))
                    cur_cols = cur.description
                    for r in cur:
                        for i in range(0,len(cur_cols)):
                            print( cur_cols[i][0].ljust(32), ':', r[i] )

                
                print(f'Check index {idx_name}:')
                with act.db.connect() as con1, act.db.connect() as con2:
                    tx1 = con1.transaction_manager(custom_tpb)
                    tx2 = con2.transaction_manager(custom_tpb)
                    tx1.begin()
                    tx2.begin()
                    with tx1.cursor() as cur1, tx2.cursor() as cur2:
                        try:
                            # DML 'insert into ... select from ...'. Index {idx_name} must be involved:
                            msg = 'att-1, point-1'
                            cur1.execute(f'insert into {tt_name}(x, y) select mod(n,19), mod(n,17)  from generate_series(1, 300) as s(n)')
                            cur1.execute(f"insert into {tt_name}(y) /* {msg} */ select mod(y,31) * mod(y,29) from {tt_name} where x between ? and ?", (7, 13))

                            # Print explained plan with padding eash line by dots in order to see indentations:
                            print(msg)
                            print( '\n'.join([replace_leading(s) for s in cur1.statement.detailed_plan.split('\n')]) )

                            cur2.execute(f'insert into {tt_name}(x, y) select -mod(n,19), -mod(n,17) from generate_series(1, 100) as s(n)')
                            cur2.execute(f'drop index /* att-2, point-1 */ {idx_name}')
                            # <<< !DO NOT COMMIT! >>>

                            # +++++++++++++++++++++++++++++ [ 1 ] +++++++++++++++++++++++++++++
                            for r in cur1:
                                pass
                            msg = 'att-1, point-2'
                            cur1.execute(f"select /* {msg} */ count(*) from rdb$indices where rdb$index_name = ?", (idx_name.upper(),))
                            print(msg)
                            for r in cur1:
                                print(f'Index "{idx_name}" found in ATT-1 ? =>', r[0])

                            # Index {idx_name} must be still involved for ATT-1:
                            msg = 'att-1, point-3'
                            cur1.execute(f"select /* {msg} */ count(*) from {tt_name} where x between ? and ?", (11, 13))
                            print(msg)
                            print( '\n'.join([replace_leading(s) for s in cur1.statement.detailed_plan.split('\n')]) )
                            for r in cur1:
                                pass

                            # +++++++++++++++++++++++++++++ [ 2 ] +++++++++++++++++++++++++++++
                            msg = 'att-2, point-2'
                            cur2.execute(f"select /* {msg} */ count(*) from rdb$indices where rdb$index_name = ?", (idx_name.upper(),))
                            print(msg)
                            for r in cur2:
                                print(f'Index "{idx_name}" found in ATT-2 ? =>', r[0])

                            # Only NR (natural reads) must be avaliable now for ATT-2:
                            msg = 'att-2, point-3'
                            cur2.execute(f"select /* {msg} */ count(*) from {tt_name} where x between ? and ?", (-18, -17))
                            print(msg)
                            print( '\n'.join([replace_leading(s) for s in cur2.statement.detailed_plan.split('\n')]) )
                            for r in cur2:
                                pass

                            tx2.rollback() # <<< this must allow ATT-2 again to use index! But this att must add records again.
                            # +++++++++++++++++++++++++++++ [ 3 ] +++++++++++++++++++++++++++++
                            tx2.begin()

                            msg = 'att-2, point-4'
                            cur2.execute(f"select /* {msg} */ count(*) from rdb$indices where rdb$index_name = ?", (idx_name.upper(),))
                            print(msg)
                            for r in cur2:
                                print(f'Index "{idx_name}" found in ATT-2 ? =>', r[0])

                            # IR (indexed reads) must be again avaliable now for ATT-2:
                            msg = 'att-2, point-5'
                            cur2.execute(f'insert into {tt_name}(x, y) select -mod(n,19), -mod(n,17) from generate_series(1, 100) as s(n)')
                            cur2.execute(f"select /* {msg} */ count(*) from {tt_name} where x between ? and ?", (-18, -17))
                            print(msg)
                            print( '\n'.join([replace_leading(s) for s in cur2.statement.detailed_plan.split('\n')]) )
                            for r in cur2:
                                pass

                            tx1.rollback()
                            # tx2.rollback()

                        except Exception as e:
                            print(e.__str__())
                            print(e.gds_codes)
                    # < with tx1.cursor() as cur1, tx2.cursor() as cur2
                # < with act.db.connect() as con1, act.db.connect() as con2

                with act.db.connect() as con_dba:
                    con_dba.execute_immediate(f'drop index {idx_name}')
                    con_dba.commit()
            
                expected_out = f"""
                    TIL: {x_isol.name}
                    Check {tab_type=} {tt_suff}

                    REL_TYPE                         : {tt_type}
                    IDX_NAME                         : {idx_name}
                    IS_COMPUTED                      : {idx_computed}
                    IS_PARTIAL                       : {idx_partial}

                    Check index {idx_name}:
                    att-1, point-1
                    Select Expression
                    ....-> Filter
                    ........-> Table "PUBLIC"."{tt_name}" Access By ID
                    ............-> Bitmap
                    ................-> Index "PUBLIC"."{idx_name}" Range Scan (lower bound: 1/1, upper bound: 1/1)
                    att-1, point-2
                    Index "{idx_name}" found in ATT-1 ? => 1
                    att-1, point-3
                    Select Expression
                    ....-> Aggregate
                    ........-> Filter
                    ............-> Table "PUBLIC"."{tt_name}" Access By ID
                    ................-> Bitmap
                    ....................-> Index "PUBLIC"."{idx_name}" Range Scan (lower bound: 1/1, upper bound: 1/1)
                    att-2, point-2
                    Index "{idx_name}" found in ATT-2 ? => 0
                    att-2, point-3
                    Select Expression
                    ....-> Aggregate
                    ........-> Filter
                    ............-> Table "PUBLIC"."{tt_name}" Full Scan
                    att-2, point-4
                    Index "{idx_name}" found in ATT-2 ? => 1
                    att-2, point-5
                    Select Expression
                    ....-> Aggregate
                    ........-> Filter
                    ............-> Table "PUBLIC"."{tt_name}" Access By ID
                    ................-> Bitmap
                    ....................-> Index "PUBLIC"."{idx_name}" Range Scan (lower bound: 1/1, upper bound: 1/1)
                """

                act.expected_stdout = expected_out
                act.stdout = capsys.readouterr().out
                assert act.clean_stdout == act.clean_expected_stdout
                act.reset()
            # < for idx_name, idx_opts in idx_ddl_map.items()

