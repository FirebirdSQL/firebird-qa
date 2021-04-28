#coding:utf-8
#
# id:           bugs.core_3091
# title:        Built-in function POWER(X, Y) does not work when the X argument is negative and the Y value is scaled numeric but integral
# decription:   
# tracker_id:   CORE-3091
# min_versions: ['2.1.4']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select 'power( 3, 2 )', power( 3, 2 ) from RDB$DATABASE
union all
select 'power( -3, 2 )', power( -3, 2 ) from RDB$DATABASE
union all
select 'power( 3, -2 )', power( 3, -2 ) from RDB$DATABASE
union all
select 'power( -3, -2 )', power( -3, -2 ) from RDB$DATABASE
union all
select 'power( 3, 2.0 )', power( 3, 2.0 ) from RDB$DATABASE
union all
select 'power( 3, -2.0 )', power( 3, -2.0 ) from RDB$DATABASE
union all
select 'power( -3, 2.0 )', power( -3, 2.0 ) from RDB$DATABASE
union all
select 'power( -3, -2.0 )', power( -3, -2.0 ) from RDB$DATABASE
union all
select 'power( -3.0, 2 )', power( -3.0, 2 ) from RDB$DATABASE
union all
select 'power( -3.0, 2.0 )', power( -3.0, 2.0 ) from RDB$DATABASE
union all
select 'power( -3.0, -2.0 )', power( -3.0, -2.0 ) from RDB$DATABASE
union all
select 'power( 3.0, -2.0 )', power( 3.0, -2.0 ) from RDB$DATABASE
union all
select 'power( 3.0, 2.0 )', power( 3.0, 2.0 ) from RDB$DATABASE
union all
select 'power( 3.0, 2 )', power( 3.0, 2 ) from RDB$DATABASE
union all
select 'power( 3.0, -2 )', power( 3.0, -2 ) from RDB$DATABASE
;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """

=================== =======================
power( 3, 2 )             9.000000000000000
power( -3, 2 )            9.000000000000000
power( 3, -2 )           0.1111111111111111
power( -3, -2 )          0.1111111111111111
power( 3, 2.0 )           9.000000000000000
power( 3, -2.0 )         0.1111111111111111
power( -3, 2.0 )          9.000000000000000
power( -3, -2.0 )        0.1111111111111111
power( -3.0, 2 )          9.000000000000000
power( -3.0, 2.0 )        9.000000000000000
power( -3.0, -2.0 )      0.1111111111111111
power( 3.0, -2.0 )       0.1111111111111111
power( 3.0, 2.0 )         9.000000000000000
power( 3.0, 2 )           9.000000000000000
power( 3.0, -2 )         0.1111111111111111

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

