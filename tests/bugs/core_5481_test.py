#coding:utf-8
#
# id:           bugs.core_5481
# title:        Available indices are not used in some cases if ORDER BY expression is a filtered one
# decription:   
#                     Confirmed bug on WI-V3.0.1.32609:
#                         1. Plan when FK did present was ineffective: PLAN (V_TEST B ORDER BALANCES_BALANCEDATE_DESC)
#                         2. Effective plan was in use only after dropping FK.
#                     Checked on: 3.0.5.33084, 4.0.0.1340 - works fine.
#                 
# tracker_id:   CORE-5481
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (V_TEST B ORDER BALANCES_BALANCEDATE_DESC INDEX (FK_BALANCES_ORGACCOUNTS))
    PLAN (V_TEST B ORDER BALANCES_BALANCEDATE_DESC INDEX (FK_BALANCES_ORGACCOUNTS))
"""

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

