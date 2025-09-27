#coding:utf-8

"""
ID:          n/a
TITLE:       
DESCRIPTION:
  Original test see in:
      https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/C_SQL_PRED_1.script
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
    where not singular (select * from customers c2 where c1.custno = c2.custno)
    ;
    set count off;
    select 'point-01' as msg from rdb$database;

    set count on;
    select * from customers c1
    where
        1 < (select count(*) from customers c2 where c1.custno = c2.custno)
        or 0 = (select count(*) from customers c3 where c3.custno = c3.custno)
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

        Records affected: 0
        MSG point-01

        Records affected: 0
        MSG point-02
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
