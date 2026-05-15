#coding:utf-8

"""
ID:          n/a
ISSUE:       Shared metacache. Mailbox p519446@yandex.com, letter to FB-team 20.04.2026 1516
TITLE:       DROP TABLE caused "page 0 is of wrong type (expected index root, found database header)"
DESCRIPTION:
    Problem was encountered during re-implementing test for CORE-3188, 6.x CLASSIC.
    Initial report to to FB-team: 20.04.2026 1516.
NOTES:
    [15.05.2026] pzotov
    Reproduced on CS at leat up to 6.0.0.1947.
    On Super this problem did not exist (checked on 6.0.0.1771 - first snapshot with shared metacache).
    Waiting for fix for CLASSIC.
"""
import time
from firebird.driver import tpb, Isolation, TraAccessMode, DatabaseError

import pytest
from firebird.qa import *
db = db_factory()
act = python_act('db')

MAX_TIMEOUT = 5
EXPECTED_MSG = 'Completed.'

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    custom_tpb = tpb(isolation=Isolation.SNAPSHOT, access_mode=TraAccessMode.WRITE, lock_timeout = -1)

    with act.db.connect() as con:
        tx1a = con.transaction_manager(custom_tpb)
        tx1a.begin()
        tx1 = con.transaction_manager(custom_tpb)
        cu1 = tx1.cursor()
        with act.db.connect() as con2:
            tx2a = con2.transaction_manager(custom_tpb)
            tx2a.begin()
            tx2 = con2.transaction_manager(custom_tpb)
            cu2 = tx2.cursor()

            cu1.execute('recreate table test(id int primary key)')
            tx1.commit()

            cu2.execute('drop table test')
            tx2.commit()

    act.expected_stdout = f"""
    """

    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
