#coding:utf-8

"""
ID:          issue-5751
ISSUE:       5751
TITLE:       Available indices are not used in some cases if ORDER BY expression is a filtered one
DESCRIPTION:
JIRA:        CORE-5481
FBTEST:      bugs.core_5481
NOTES:
    [24.09.2023] pzotov
    Execution plan changed in FB 5.x since build 5.0.0.1211 (14-sep-2023).
    Expected output has been splitted on that remains actual for FB 4.x and one that issued for 5.x+.
    Confirmed by dimitr, letter 24.09.2023 13:30
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate view v_test as select 1 x from rdb$database;
    commit;
    recreate table balances
    (
        balanceid bigint not null,
        orgaccountid bigint not null,
        balancedate date not null
    );

    recreate table org_accounts
    (
        orgaccountid bigint not null primary key
    );

    alter table balances add constraint pk_balances primary key (balanceid);
    alter table balances add constraint fk_balances_orgaccounts foreign key (orgaccountid) references org_accounts (orgaccountid);
    alter table balances add constraint balances_balancedate_orgaccount unique (orgaccountid, balancedate);

    create descending index balances_balancedate_desc on balances (balancedate);

    recreate view v_test as
    select b.*
    from balances b
    where
        orgaccountid=18 and
        balancedate<='01.01.2017'
    order by balancedate desc
    rows 1
    ;
    commit;

    set plan on;
    select * from v_test;
    commit;

    ALTER TABLE BALANCES DROP CONSTRAINT BALANCES_BALANCEDATE_ORGACCOUNT;
    commit;

    select * from v_test; -- plan here should remains the same!
    commit;
"""

act = isql_act('db', test_script)

expected_stdout_4x = """
    PLAN (V_TEST B ORDER BALANCES_BALANCEDATE_DESC INDEX (FK_BALANCES_ORGACCOUNTS))
    PLAN (V_TEST B ORDER BALANCES_BALANCEDATE_DESC INDEX (FK_BALANCES_ORGACCOUNTS))
"""

expected_stdout_5x = """
    PLAN SORT (V_TEST B INDEX (BALANCES_BALANCEDATE_ORGACCOUNT))
    PLAN (V_TEST B ORDER BALANCES_BALANCEDATE_DESC INDEX (FK_BALANCES_ORGACCOUNTS))
"""

@pytest.mark.version('>=3.0.4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_4x if act.is_version('<5') else expected_stdout_5x
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

