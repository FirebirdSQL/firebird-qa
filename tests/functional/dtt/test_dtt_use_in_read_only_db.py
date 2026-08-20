#coding:utf-8

"""
ID:          n/a
TITLE:       DECLARED TEMPORARY TABLE must be updatable in read-only database
DESCRIPTION:
    Test changes DB access mode to READ ONLY and verifies that execute block:
    * can declare DTT (declared temporary table);
    * can run INSERT / UPDATE / DELETE statements against this table (by check ROW_COUNT result of each DML).
    This check is performed for each Tx isolation level. Transactions are defined as READ-ONLY.
NOTES:
    [20.08.2026] pzotov
    ::: NOTE :::
    The `MERGE` statement currently is not tested because it changes ROW_COUNT always to 1, see:
    https://github.com/FirebirdSQL/firebird/issues/4722
    Checked on 6.0.0.2153-5a5b8a2.
"""
import locale
import time
from pathlib import Path

import pytest
from firebird.qa import *
from firebird.driver import DatabaseError, tpb, TraAccessMode, Isolation

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    act.gfix(switches=['-mode','read_only', act.db.dsn], combine_output = True, io_enc = locale.getpreferredencoding())
    assert act.return_code == 0 and act.stdout == ''

    check_dml = """
        execute block returns(ins_cnt int, upd_cnt int, del_cnt int) as
            declare temporary table dtt_test (id int not null);
        begin
            insert into dtt_test(id) select s.i from generate_series(0,999) as s(i);
            ins_cnt = row_count;
            update dtt_test set id = -id where mod(id,3) = 0;
            upd_cnt = row_count;

            delete from dtt_test where abs(id) <= 100;
            del_cnt = row_count;

            /*
            -- Currently NOT fixed:
            -- https://github.com/FirebirdSQL/firebird/issues/4722
            merge into dtt_test t
            using ( select s.i from generate_series(900, 1100) as s(i) ) s on s.i = t.id
            when MATCHED then -- 66
                update set t.id = s.i * 10
            when NOT matched then -- 1 ?!
                insert values(s.i)
            ;
            mer_cnt = row_count;
            */

            suspend;
        end
        ^
    """

    tx_isol_lst = [ Isolation.READ_COMMITTED_NO_RECORD_VERSION,
                    Isolation.READ_COMMITTED_RECORD_VERSION,
                    Isolation.READ_COMMITTED_READ_CONSISTENCY,
                    Isolation.SNAPSHOT,
                    Isolation.SERIALIZABLE,
                  ]

    for x_isol in tx_isol_lst:
    
        custom_tpb = tpb(isolation = x_isol, access_mode=TraAccessMode.READ, lock_timeout = 0)

        print(x_isol.name)
        try:
            with act.db.connect() as con:
                tx = con.transaction_manager(custom_tpb)
                cur = tx.cursor()
                tx.begin()
                for line in check_dml.split('^'):
                    if (s := line.strip()):
                        cur.execute(s)
                        for r in cur:
                            for i,col in enumerate(cur.description):
                                print((col[0] +':').ljust(32), r[i])
                tx.rollback()
        except DatabaseError as e:
            print(e.__str__())
            print(e.gds_codes)

        act.expected_stdout = f"""
            {x_isol.name}
            INS_CNT: 1000
            UPD_CNT: 334
            DEL_CNT: 101
        """
       
        act.stdout = capsys.readouterr().out
        assert act.clean_stdout == act.clean_expected_stdout
        act.reset()
