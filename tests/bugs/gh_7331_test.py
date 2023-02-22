#coding:utf-8

"""
ID:          issue-7331
ISSUE:       7331
TITLE:       Cost-based choice between nested loop join and hash join
NOTES:
    [20.02.2023] pzotov
    Confirmed difference between snapshots before and after commit
    https://github.com/FirebirdSQL/firebird/commit/99c9f63f874d74beb53d338c97c033fe7c8d71a9
    Checked on 5.0.0.763 (plan did not use hash join); 5.0.0.957 (plan uses HJ).
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table customer(
         c_custkey int not null
    );

    recreate table orders(
         o_orderkey int not null
        ,o_custkey int not null
        ,o_orderdate date
    );

    recreate table lineitem(
         l_itemkey int not null
        ,l_orderkey int not null
        ,l_shipdate date
    );


    insert into customer(c_custkey)
    select row_number()over() i
    from rdb$types
    rows 100
    ;

    insert into orders(o_orderkey, o_custkey, o_orderdate)
    select i, c_custkey, o_orderdate
    from (
         select row_number()over() i, c.c_custkey, dateadd(t.i day to date '10.03.1995') o_orderdate
         from customer c
         cross join (select row_number()over() i from rdb$types rows 100) t
    )
    ;

    insert into lineitem(
         l_itemkey
        ,l_orderkey
        ,l_shipdate
    )
    select i, o_orderkey, l_shipdate
    from (
         select row_number()over() i, o.o_orderkey, dateadd(t.i day to date '10.03.1995') l_shipdate
         from orders o
         cross join (select row_number()over() i from rdb$types rows 10) t
    )
    ;
    commit;

    alter table customer
        add constraint customer_custkey_pk primary key(c_custkey)
    ;
    alter table orders
        add constraint orders_orderkey_pk primary key(o_orderkey)
    ;
    alter table orders
        add constraint orders_custkey_fk foreign key(o_custkey) references customer
    ;

    alter table lineitem
        add constraint lineitem_itemkey_pk primary key(l_itemkey)
    ;
    alter table lineitem
        add constraint lineitem_orders_fk foreign key(l_orderkey) references orders
    ;

    create index orders_date on orders(o_orderdate);
    create index lineitem_shipdate on lineitem(l_shipdate);
    commit;


    set planonly on;

    select *
    from
       orders, lineitem
    where
       l_orderkey = o_orderkey
       and l_shipdate between date '1995-03-15' and date '2000-03-15';

    select *
    from
       customer, orders, lineitem
    where
       c_custkey = o_custkey
       and l_orderkey = o_orderkey
       and l_shipdate between date '1995-03-15' and date '2000-03-15';

"""

act = isql_act('db', test_script)

expected_stdout = """
    PLAN HASH (LINEITEM INDEX (LINEITEM_SHIPDATE), ORDERS NATURAL)
    PLAN HASH (LINEITEM INDEX (LINEITEM_SHIPDATE), JOIN (CUSTOMER NATURAL, ORDERS INDEX (ORDERS_CUSTKEY_FK)))
"""

@pytest.mark.version('>=5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
