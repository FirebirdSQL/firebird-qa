#coding:utf-8

"""
ID:          n/a
TITLE:       Support for NOT SINGULAR when subquery refers to another table
DESCRIPTION:
    Original test see in:
    https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/C_SQL_PRED_4.script
NOTES:
    [27.09.2025] pzotov
    ::: NB :::
    Relation 'sales' after restore will have duplicates in rdb$relation_fields.rdb$field_position.
    Query "select * from sales ..." will produce columns in DIFFERENT ORDER on 3.x vs 4.x+.
    Because of that, one need to explicitly specify columns which we want to display - see code below.

    Checked on 6.0.0.1282; 5.0.4.1715; 4.0.7.3235; 3.0.14.33826.
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup = 'gtcs_sh_test.fbk')

test_script = """
    set list on;
    select 'point-00' as msg from rdb$database;
    set count on;
    select 1 from sales s1
    where not singular (select * from customers c1 where c1.custno =s1.custno)
    ;
    set count off;
    select 'point-01' as msg from rdb$database;
    set count on;
    select 1 from sales s1
    where
        0 = (select count(*) from customers c1 where c1.custno =s1.custno)
        or 1 < (select count(*) from customers c2 where c2.custno =s1.custno)
    ;
    set count off;
    select 'point-02' as msg from rdb$database;
    set count on;

    -- ################################################
    -- ### ACHTUNG: DO NOT USE '*' HERE.            ###
    -- ### ORDER OF COLUMNS IN RESTORED DATABASE    ###
    -- ### DIFFERS FOR TABLE 'SALES' ON 3.X VS 4.X+ ###
    -- ################################################
    select
        warranty
        ,custno
        ,ponumb
        ,sales_rep
        ,aged
        ,order_date
        ,total_value
        ,date_needed
        ,order_status
        ,paid
        ,shipped 
    from sales s1 
    where singular (select * from customers c1 where c1.custno =s1.custno)
    order by s1.ponumb -- sales has index: PO UNIQUE INDEX ON SALES(PONUMB)
    ;
    set count off;
    select 'point-03' as msg from rdb$database;
    set count on;
    -- show table sales;
    -- show index sales;
"""

substitutions = [ ('[ \t]+', ' '), ]
act = isql_act('db', test_script, substitutions = substitutions)

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = """
        MSG point-00

        Records affected: 0
        MSG point-01
        
        Records affected: 0
        MSG point-02
        
        WARRANTY 04-SEP-1989
        CUSTNO 103
        PONUMB 89010401
        SALES_REP 100
        AGED 13217
        ORDER_DATE 18-JUL-1989
        TOTAL_VALUE 53000
        DATE_NEEDED 01-AUG-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 21-JUL-1989
        WARRANTY 04-SEP-1989
        CUSTNO 100
        PONUMB 89010402
        SALES_REP 118
        AGED 13217
        ORDER_DATE 18-JUL-1989
        TOTAL_VALUE 5500
        DATE_NEEDED 01-AUG-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 21-JUL-1989
        WARRANTY 04-SEP-1989
        CUSTNO 109
        PONUMB 89010403
        SALES_REP 125
        AGED 13217
        ORDER_DATE 18-JUL-1989
        TOTAL_VALUE 15500
        DATE_NEEDED 01-AUG-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 21-JUL-1989
        WARRANTY 14-SEP-1989
        CUSTNO 101
        PONUMB 89011401
        SALES_REP 100
        AGED 13207
        ORDER_DATE 28-JUL-1989
        TOTAL_VALUE 48500
        DATE_NEEDED 11-AUG-1989
        ORDER_STATUS shipped
        PAID <null>
        SHIPPED 31-JUL-1989
        WARRANTY 21-SEP-1989
        CUSTNO 102
        PONUMB 89011501
        SALES_REP 125
        AGED 13200
        ORDER_DATE 29-JUL-1989
        TOTAL_VALUE 18500
        DATE_NEEDED 12-AUG-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 07-AUG-1989
        WARRANTY 18-OCT-1989
        CUSTNO 103
        PONUMB 89021301
        SALES_REP 100
        AGED 13173
        ORDER_DATE 27-AUG-1989
        TOTAL_VALUE 8000
        DATE_NEEDED 10-SEP-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 03-SEP-1989
        WARRANTY 18-OCT-1989
        CUSTNO 104
        PONUMB 89021302
        SALES_REP 137
        AGED 13173
        ORDER_DATE 27-AUG-1989
        TOTAL_VALUE 38000
        DATE_NEEDED 10-SEP-1989
        ORDER_STATUS shipped
        PAID <null>
        SHIPPED 03-SEP-1989
        WARRANTY 23-OCT-1989
        CUSTNO 105
        PONUMB 89022201
        SALES_REP 125
        AGED 13168
        ORDER_DATE 05-SEP-1989
        TOTAL_VALUE 25500
        DATE_NEEDED 19-SEP-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 08-SEP-1989
        WARRANTY 26-OCT-1989
        CUSTNO 106
        PONUMB 89022301
        SALES_REP 137
        AGED 13165
        ORDER_DATE 06-SEP-1989
        TOTAL_VALUE 18000
        DATE_NEEDED 20-SEP-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 11-SEP-1989
        WARRANTY 04-NOV-1989
        CUSTNO 107
        PONUMB 89030301
        SALES_REP 100
        AGED 13156
        ORDER_DATE 14-SEP-1989
        TOTAL_VALUE 8000
        DATE_NEEDED 28-SEP-1989
        ORDER_STATUS shipped
        PAID <null>
        SHIPPED 20-SEP-1989
        WARRANTY 04-NOV-1989
        CUSTNO 108
        PONUMB 89030302
        SALES_REP 125
        AGED 13156
        ORDER_DATE 14-SEP-1989
        TOTAL_VALUE 48500
        DATE_NEEDED 28-SEP-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 20-SEP-1989
        WARRANTY 02-NOV-1989
        CUSTNO 109
        PONUMB 89030303
        SALES_REP 125
        AGED 13158
        ORDER_DATE 14-SEP-1989
        TOTAL_VALUE 43500
        DATE_NEEDED 28-SEP-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 18-SEP-1989
        WARRANTY 02-NOV-1989
        CUSTNO 110
        PONUMB 89030304
        SALES_REP 100
        AGED 13158
        ORDER_DATE 14-SEP-1989
        TOTAL_VALUE 4500
        DATE_NEEDED 28-SEP-1989
        ORDER_STATUS shipped
        PAID *
        SHIPPED 18-SEP-1989
        WARRANTY 21-NOV-1989
        CUSTNO 111
        PONUMB 89031601
        SALES_REP 118
        AGED 13139
        ORDER_DATE 27-SEP-1989
        TOTAL_VALUE 14500
        DATE_NEEDED 11-OCT-1989
        ORDER_STATUS shipped
        PAID <null>
        SHIPPED 07-OCT-1989
        WARRANTY <null>
        CUSTNO 112
        PONUMB 89032601
        SALES_REP 100
        AGED <null>
        ORDER_DATE 07-OCT-1989
        TOTAL_VALUE 19500
        DATE_NEEDED 21-OCT-1989
        ORDER_STATUS waiting
        PAID <null>
        SHIPPED <null>
        WARRANTY <null>
        CUSTNO 113
        PONUMB 89032602
        SALES_REP 137
        AGED <null>
        ORDER_DATE 07-OCT-1989
        TOTAL_VALUE 85000
        DATE_NEEDED 21-OCT-1989
        ORDER_STATUS waiting
        PAID <null>
        SHIPPED <null>
        Records affected: 16
        MSG point-03
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
