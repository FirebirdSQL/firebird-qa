#coding:utf-8
#
# id:           bugs.core_0625
# title:        Token unknown in simple SELECT with GROUP BY and ORDER BY
# decription:   getting SQL error code = -104, Token unknown count.
# tracker_id:   CORE-0625
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = [('\\(+', ''), ('\\)+', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN SORT CUSTOMERS ORDER CUSTOMERS_COUNTRY
  """

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

