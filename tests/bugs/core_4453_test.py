#coding:utf-8

"""
ID:          issue-4773
ISSUE:       4773
TITLE:       Regression: NOT NULL constraint, declared in domain, does not work
DESCRIPTION:
JIRA:        CORE-4453
FBTEST:      bugs.core_4453
"""

import pytest
from firebird.qa import *

init_script = """
    -- Tests that manipulates with NULL fields/domains and check results:
    -- CORE-1518 Adding a non-null restricted column to a populated table renders the table inconsistent
    -- CORE-4453 (Regression: NOT NULL constraint, declared in domain, does not work)
    -- CORE-4725 (Inconsistencies with ALTER DOMAIN and ALTER TABLE with DROP NOT NULL and PRIMARY KEYs)
    -- CORE-4733 (Command "Alter table <T> alter TYPE <C> <DOMAIN_WITH_NOT_NULL" does not verifies data in column <C> and makes incorrect assignments in <C> to ZERO / JULIAN_DATE / ASCII(0) for types INT, TIMESTAMP and VARCHAR)
    create domain dm_01 varchar(20) not null;
    commit;
    create table t_01(s dm_01, x int);
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    insert into t_01(x) values(100);
    select * from t_01 where s is null;
"""

act = isql_act('db', test_script)

expected_stderr = """
    Statement failed, SQLSTATE = 23000
    validation error for column "T_01"."S", value "*** null ***"
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

