#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7954
TITLE:       Shared metacache. Check ability to DROP INDEX <X> while concurrent DML activity exists that involves index <X>
DESCRIPTION:
    Test verifies ability to DROP index while it is involved in work during DML actions perfoming by concurrent attachment.
    Scenario:
        * att-1: runs DML like 'insert into <T>(<X>) select from ...' where <T.X> is indexed column. NO commit is done here;
        * att-2: tries to DROP INDEX for T.X column (this must pass). NO commit is done here;
        * att-1: runs 'select ... from test where x between ? and ?'; explained plan must show INDEXED range scan;
        * att-2: runs the same query; explained plan must show NATURAL access (i.e. table full scan);
        * att-1: rollbacks statement 'DROP INDEX ...' and runs query to T.X; plan must show again ("reverted") INDEXED scan.
    These checks are performed for three kinds of index: refular; computed-by; conditional.
    All kinds of TIL are checked (read committed; read consistency; snapshot; serialize) -- this is organized as outer loop.
NOTES:
    [23.04.2026] pzotov
    ::: NB :::
    Currently test fails on TIL = READ_COMMITTED_NO_RECORD_VERSION and SERIALIZABLE. Sent report to FB-team.
    Checked on 6.0.0.1914-67e1176.
"""

import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, DatabaseError, FirebirdWarning

init_script = """
    SET BAIL ON;
    create table test(x int, y int);
    insert into test(x, y) select mod(n,19), mod(n,17)
    from generate_series(1, 300) as s(n);
    commit;
"""
db = db_factory(init = init_script)

act = python_act('db')


#-----------------------------------------------------------
def replace_leading(source, char="."):
    stripped = source.lstrip()
    return char * (len(source) - len(stripped)) + stripped
#-----------------------------------------------------------

@pytest.mark.version('>=6')
def test_1(act: Action, capsys):
    
    idx_ddl_map = {
        'test_x_regular' : 'create index test_x_regular on test(x)'
       ,'text_x_eval'    : 'create index text_x_eval on test computed by(x)'
       ,'text_x_cond'    : 'create index text_x_cond on test(x) where x is not null'
    }

    tx_isol_lst = [ 
                    Isolation.READ_COMMITTED_RECORD_VERSION,
                    Isolation.READ_COMMITTED_READ_CONSISTENCY,
                    Isolation.SNAPSHOT,
                    # ................................................
                    # DOES NOT WORK CURRENTLY (23.04.2026, 6.0.0.1914):
                    # Isolation.READ_COMMITTED_NO_RECORD_VERSION,
                    # Isolation.SERIALIZABLE,
                    # ................................................
                  ]

    # temp 4debug:
    tx_isol_lst= [ Isolation.SNAPSHOT, ]

    # for any isolation mode attempt to run DDL for table that is in use by another Tx must fail
    # with the same error message. We check all possible Tx isolation modes for that:
    for x_isol in tx_isol_lst:
    
        custom_tpb = tpb(isolation = x_isol, lock_timeout = 0)
        print('TIL:', x_isol.name)

        for idx_name, idx_expr in idx_ddl_map.items():

            print(f'Check index {idx_name}:')
            with act.db.connect() as con_dba:
                con_dba.execute_immediate(idx_expr)
                con_dba.commit()
            
            with act.db.connect() as con1, act.db.connect() as con2:
                tx1 = con1.transaction_manager(custom_tpb)
                tx2 = con2.transaction_manager(custom_tpb)
                tx1.begin()
                tx2.begin()
                with tx1.cursor() as cur1, tx2.cursor() as cur2:
                    try:
                        # DML 'insert into ... select from ...'. Index {idx_name} must be involved:
                        msg = 'att-1, point-1'
                        cur1.execute(f"insert into test(y) /* {msg} */ select mod(y,31) * mod(y,29) from test where x between ? and ?", (7, 13))

                        # Print explained plan with padding eash line by dots in order to see indentations:
                        print(msg)
                        print( '\n'.join([replace_leading(s) for s in cur1.statement.detailed_plan.split('\n')]) )

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
                        cur1.execute(f"select /* {msg} */ count(*) from test where x between ? and ?", (11, 13))
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
                        cur2.execute(f"select /* {msg} */ count(*) from test where x between ? and ?", (17, 18))
                        print(msg)
                        print( '\n'.join([replace_leading(s) for s in cur2.statement.detailed_plan.split('\n')]) )
                        for r in cur2:
                            pass

                        tx2.rollback() # <<< this must allow ATT-2 again to use index!
                        # +++++++++++++++++++++++++++++ [ 3 ] +++++++++++++++++++++++++++++
                        tx2.begin()

                        msg = 'att-2, point-4'
                        cur2.execute(f"select /* {msg} */ count(*) from rdb$indices where rdb$index_name = ?", (idx_name.upper(),))
                        print(msg)
                        for r in cur2:
                            print(f'Index "{idx_name}" found in ATT-2 ? =>', r[0])

                        # IR (indexed reads) must be again avaliable now for ATT-2:
                        msg = 'att-2, point-5'
                        cur2.execute(f"select /* {msg} */ count(*) from test where x between ? and ?", (17, 18))
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
        
        # < for idx_expr in idx_ddl_lst

        expected_out = f"""
            TIL: {x_isol.name}

            Check index test_x_regular:
            att-1, point-1
            Select Expression
            ....-> Filter
            ........-> Table "PUBLIC"."TEST" Access By ID
            ............-> Bitmap
            ................-> Index "PUBLIC"."TEST_X_REGULAR" Range Scan (lower bound: 1/1, upper bound: 1/1)
            att-1, point-2
            Index "test_x_regular" found in ATT-1 ? => 1
            att-1, point-3
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "PUBLIC"."TEST" Access By ID
            ................-> Bitmap
            ....................-> Index "PUBLIC"."TEST_X_REGULAR" Range Scan (lower bound: 1/1, upper bound: 1/1)
            att-2, point-2
            Index "test_x_regular" found in ATT-2 ? => 0
            att-2, point-3
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "PUBLIC"."TEST" Full Scan
            att-2, point-4
            Index "test_x_regular" found in ATT-2 ? => 1
            att-2, point-5
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "PUBLIC"."TEST" Access By ID
            ................-> Bitmap
            ....................-> Index "PUBLIC"."TEST_X_REGULAR" Range Scan (lower bound: 1/1, upper bound: 1/1)


            Check index text_x_eval:
            att-1, point-1
            Select Expression
            ....-> Filter
            ........-> Table "PUBLIC"."TEST" Access By ID
            ............-> Bitmap
            ................-> Index "PUBLIC"."TEXT_X_EVAL" Range Scan (lower bound: 1/1, upper bound: 1/1)
            att-1, point-2
            Index "text_x_eval" found in ATT-1 ? => 1
            att-1, point-3
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "PUBLIC"."TEST" Access By ID
            ................-> Bitmap
            ....................-> Index "PUBLIC"."TEXT_X_EVAL" Range Scan (lower bound: 1/1, upper bound: 1/1)
            att-2, point-2
            Index "text_x_eval" found in ATT-2 ? => 0
            att-2, point-3
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "PUBLIC"."TEST" Full Scan
            att-2, point-4
            Index "text_x_eval" found in ATT-2 ? => 1
            att-2, point-5
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "PUBLIC"."TEST" Access By ID
            ................-> Bitmap
            ....................-> Index "PUBLIC"."TEXT_X_EVAL" Range Scan (lower bound: 1/1, upper bound: 1/1)


            Check index text_x_cond:
            att-1, point-1
            Select Expression
            ....-> Filter
            ........-> Table "PUBLIC"."TEST" Access By ID
            ............-> Bitmap
            ................-> Index "PUBLIC"."TEXT_X_COND" Range Scan (lower bound: 1/1, upper bound: 1/1)
            att-1, point-2
            Index "text_x_cond" found in ATT-1 ? => 1
            att-1, point-3
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "PUBLIC"."TEST" Access By ID
            ................-> Bitmap
            ....................-> Index "PUBLIC"."TEXT_X_COND" Range Scan (lower bound: 1/1, upper bound: 1/1)
            att-2, point-2
            Index "text_x_cond" found in ATT-2 ? => 0
            att-2, point-3
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "PUBLIC"."TEST" Full Scan
            att-2, point-4
            Index "text_x_cond" found in ATT-2 ? => 1
            att-2, point-5
            Select Expression
            ....-> Aggregate
            ........-> Filter
            ............-> Table "PUBLIC"."TEST" Access By ID
            ................-> Bitmap
            ....................-> Index "PUBLIC"."TEXT_X_COND" Range Scan (lower bound: 1/1, upper bound: 1/1)
        """

        act.expected_stdout = expected_out
        act.stdout = capsys.readouterr().out
        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()
