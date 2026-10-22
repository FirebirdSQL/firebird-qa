# coding:utf-8

"""
ID:          n/a
TITLE:       Drop tablespace must be allowed if there is an active Tx which removed all objects dependent on <TS>
DESCRIPTION:
    Test creates TS and a table within it, with adding one record in this table.
    Then we start Tx and delete record, drop table and try to drop TS.
    No error must occur. Before fix, attempt top drop TS caused 'Object in use'.
NOTES:
    [22.10.2026] pzotov
    https://github.com/FirebirdSQL/firebird/commit/6b29da958ebdd55c0af6601af65e01b8fc6ba8d9
    Thanks to dimitr for suggestion about this test scenario (letters since 21.10.2026 08:24).
    Confirmed bug on 6.0.0.2401-454db12.
    Checked on 6.0.0.2405-6b29da9 (SS/CS).
"""
import pytest
from firebird.qa import *
from firebird.driver import tpb, Isolation, DatabaseError

init_script = f"""
    create tablespace ts1 file 'ts_tmp.dat';
    commit;
    create table test_table(
        id int primary key
    )
    in tablespace ts1
    ;
    commit;
    insert into test_table values (1);
    commit;
"""

db = db_factory(init = init_script)
act = python_act('db')

expected_stdout = """
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    tx_isol_lst = [ Isolation.READ_COMMITTED_NO_RECORD_VERSION,
                    Isolation.READ_COMMITTED_RECORD_VERSION,
                    Isolation.READ_COMMITTED_READ_CONSISTENCY,
                    Isolation.SNAPSHOT,
                    Isolation.SERIALIZABLE,
                  ]

    for x_isol in tx_isol_lst:
        with act.db.connect() as con:
            custom_tpb = tpb(isolation = x_isol, lock_timeout=0)
            tx1 = con.transaction_manager(custom_tpb)
            tx1.begin()
            cur1 = tx1.cursor()
            try:
                ##########################
                ### CLEANUP, MUST PASS ###
                ##########################
                cur1.execute('delete from test_table')
                cur1.execute('drop table test_table')
                cur1.execute('drop tablespace ts1')
            except DatabaseError as e:
                print(f'Failed cleanup on TIL={x_isol.name}, {type(e).__name__}:')
                print(e.__str__())
                print(e.gds_codes)
            finally:
                tx1.rollback()

    act.stdout = capsys.readouterr().out
    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
