#coding:utf-8

"""
ID:          issue-987
ISSUE:       987
TITLE:       Token unknown in simple SELECT with GROUP BY and ORDER BY
DESCRIPTION: Getting SQL error code = -104, Token unknown count.
JIRA:        CORE-625
FBTEST:      bugs.core_0625
"""

import pytest
from firebird.qa import *

db = db_factory(page_size=4096)

test_script = """
    recreate table customers(cust_id int primary key using index customers_pk, country int);
    commit;

    insert into customers
    select r.rdb$relation_id, rand()*10
    from rdb$relations r;
    commit;

    create index customers_country on customers(country);
    commit;

    set planonly;
    --set explain on;
    select country, count(country)
    from customers
    group by country
    order by count(country);
    -- NB: PLAN up to 2.5 contains TWO parenthesis:
    -- PLAN SORT ((CUSTOMERS ORDER CUSTOMERS_COUNTRY))
    --           ^^                                 ^^
"""

act = isql_act('db', test_script, substitutions=[('\\(+', ''), ('\\)+', '')])

expected_stdout = """
    PLAN SORT CUSTOMERS ORDER CUSTOMERS_COUNTRY
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

