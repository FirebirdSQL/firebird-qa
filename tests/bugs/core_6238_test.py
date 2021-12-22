#coding:utf-8
#
# id:           bugs.core_6238
# title:        DECFLOAT: subtraction Num1 - Num2 leads to "Decimal float overflow" if Num2 is specified in scientific notation and less than max double ( 1.7976931348623157e308 )
# decription:   
#                   Checked on 4.0.0.1753: works fine.
#                
# tracker_id:   CORE-6238
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- All following statements raised before fix:
    -- Statement failed, SQLSTATE = 22003
    -- Decimal float overflow.  The exponent of a result is greater than the magnitude allowed.

    set list on;
    select (d - 1e0) as result_01 from (select 9.999999999999999999999999999999998E+6144 d from rdb$database);
    select (d - 1.79769313e308) as result_02 from (select 9.999999999999999999999999999999998E+6144 d from rdb$database);
    select (d - cast( 1e0 as float) ) as result_03  from (select 9.999999999999999999999999999999998E+6144 d from rdb$database);
    select (d + 1.79769313e-308 ) as result_04  from (select 9.999999999999999999999999999999998E+6144 d from rdb$database);

    -- This EB was added only to check that no error will be while executing statements in it.
    -- See letter to Alex, 31.01.2020 11:34, and his postfix for this ticket:
    -- https://github.com/FirebirdSQL/firebird/commit/0ef5a1a1c1bf42021b378e1691aaccfd75a454b4
    set term ^;
    execute block as
        declare dt date;
        declare tm time;
        declare ts timestamp;
    begin
        select current_date + cast(1 as numeric(19,0)) from rdb$database into dt;
        select current_date + cast(1 as decfloat) from rdb$database into dt;

        select current_time + cast(1 as numeric(19,0)) from rdb$database into tm;
        select current_time + cast(1 as decfloat) from rdb$database into tm;

        select current_timestamp + cast(1 as decfloat) from rdb$database into ts;
        select current_timestamp + cast(1 as decfloat) from rdb$database into ts;
    end
    ^
    set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT_01                        9.999999999999999999999999999999998E+6144
    RESULT_02                        9.999999999999999999999999999999998E+6144
    RESULT_03                        9.999999999999999999999999999999998E+6144
    RESULT_04                        9.999999999999999999999999999999998E+6144
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

