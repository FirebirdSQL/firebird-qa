#coding:utf-8

"""
ID:          n/a
TITLE:       
DESCRIPTION:
  Original test see in:
      https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/C_SQL_PRED_3.script
NOTES:
    [27.09.2025] pzotov
    Checked on 6.0.0.1282; 5.0.4.1715; 4.0.7.3235; 3.0.14.33826.
"""

import pytest
from firebird.qa import *

db = db_factory(from_backup = 'gtcs_sh_test.fbk')

test_script = """
    set list on;
    select 'point-00' as msg from rdb$database;
    set count on;
    select * from customers c1
    where not singular (select * from sales s1 where s1.custno = c1.custno)
    ;
    set count off;
    select 'point-01' as msg from rdb$database;
    set count on;
    select * from customers c1
    where 0 = (select count(*) from sales s1 where s1.custno = c1.custno)
    or 1 < (select count(*) from sales s2 where s2.custno = c1.custno)
    ;
    set count off;
    select 'point-02' as msg from rdb$database;
"""

substitutions = [ ('[ \t]+', ' '), ]
act = isql_act('db', test_script, substitutions = substitutions)

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = """
        MSG point-00
        CUSTNO 114
        CUSTOMER 1st Canine Bank
        CONTACT George McClellan
        ADDRESS 1342 Massachusetts Avenue
        CITY Boston
        STATE MA
        ZIP_CODE 02113
        PHONE_NO 6179291622
        ON_HOLD <null>
        CUSTNO 103
        CUSTOMER The Groton Company
        CONTACT Phil Sheridan
        ADDRESS Great Road
        CITY Groton
        STATE MA
        ZIP_CODE 01450
        PHONE_NO 5086436627
        ON_HOLD <null>
        CUSTNO 109
        CUSTOMER Czbrynik Meat Packer
        CONTACT George Meade
        ADDRESS 3 Meat Market
        CITY Green Bay
        STATE WI
        ZIP_CODE 54305
        PHONE_NO 4142983288
        ON_HOLD <null>
        Records affected: 3
        MSG point-01
        CUSTNO 114
        CUSTOMER 1st Canine Bank
        CONTACT George McClellan
        ADDRESS 1342 Massachusetts Avenue
        CITY Boston
        STATE MA
        ZIP_CODE 02113
        PHONE_NO 6179291622
        ON_HOLD <null>
        CUSTNO 103
        CUSTOMER The Groton Company
        CONTACT Phil Sheridan
        ADDRESS Great Road
        CITY Groton
        STATE MA
        ZIP_CODE 01450
        PHONE_NO 5086436627
        ON_HOLD <null>
        CUSTNO 109
        CUSTOMER Czbrynik Meat Packer
        CONTACT George Meade
        ADDRESS 3 Meat Market
        CITY Green Bay
        STATE WI
        ZIP_CODE 54305
        PHONE_NO 4142983288
        ON_HOLD <null>
        Records affected: 3
        MSG point-02
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
