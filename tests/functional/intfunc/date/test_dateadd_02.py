#coding:utf-8
#
# id:           functional.intfunc.date.dateadd_02
# title:        Test results of DATEADD function for MONTH
# decription:   Returns a date/time/timestamp value increased (or decreased, when negative) by the specified amount of time.
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         functional.intfunc.date.dateadd_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    
    -- doc\\sql.extensions\\README.builtin_functions.txt 
    -- 5) When using YEAR or MONTH and the input day is greater than the maximum possible day in the
    --    result year/month, the result day is returned in the last day of the result year/month.
    
    set list on;

    select dateadd(  1 month to date '2004-01-31') as leap_jan_31_plus__01_month from rdb$database;
    select dateadd(  1 month to date '2004-02-28') as leap_feb_28_plus__01_month from rdb$database;
    select dateadd(  1 month to date '2004-02-29') as leap_feb_29_plus__01_month from rdb$database;
    select dateadd( -1 month to date '2004-02-28') as leap_feb_28_minus_01_month from rdb$database;
    select dateadd( -1 month to date '2004-02-29') as leap_feb_29_minus_01_month from rdb$database;
    select dateadd( 11 month to date '2004-02-28') as leap_feb_28_plus__11_month from rdb$database;
    select dateadd( 11 month to date '2004-02-29') as leap_feb_29_plus__11_month from rdb$database;
    select dateadd( 12 month to date '2004-02-28') as leap_feb_28_plus__12_month from rdb$database;
    select dateadd( 12 month to date '2004-02-29') as leap_feb_29_plus__12_month from rdb$database;
    select dateadd(-11 month to date '2004-02-28') as leap_feb_28_minus_11_month from rdb$database;
    select dateadd(-11 month to date '2004-02-29') as leap_feb_29_minus_11_month from rdb$database;
    select dateadd(-12 month to date '2004-02-28') as leap_feb_28_minus_12_month from rdb$database;
    select dateadd(-12 month to date '2004-02-29') as leap_feb_29_minus_12_month from rdb$database;
    select dateadd( -1 month to date '2004-03-31') as leap_mar_31_minus_01_month from rdb$database;

    select dateadd(  1 month to date '2003-01-31') as nonl_jan_31_plus__01_month from rdb$database;
    select dateadd(  1 month to date '2003-02-28') as nonl_feb_28_plus__01_month from rdb$database;
    select dateadd( -1 month to date '2003-02-28') as nonl_feb_28_minus_01_month from rdb$database;
    select dateadd( 11 month to date '2003-02-28') as nonl_feb_28_plus__11_month from rdb$database;
    select dateadd( 12 month to date '2003-02-28') as nonl_feb_28_plus__12_month from rdb$database;
    select dateadd(-11 month to date '2003-02-28') as nonl_feb_28_minus_11_month from rdb$database;
    select dateadd(-12 month to date '2003-02-28') as nonl_feb_28_minus_12_month from rdb$database;
    select dateadd( -1 month to date '2003-03-31') as nonl_mar_31_minus_01_month from rdb$database;

    -- old test code:
    -- select dateadd(-1 month TO date '2008-02-06' ) as yesterday from rdb$database;
    -- select dateadd(month,-1, date '2008-02-06' ) as yesterday from rdb$database;
 """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    LEAP_JAN_31_PLUS__01_MONTH      2004-02-29
    LEAP_FEB_28_PLUS__01_MONTH      2004-03-28
    LEAP_FEB_29_PLUS__01_MONTH      2004-03-29
    LEAP_FEB_28_MINUS_01_MONTH      2004-01-28
    LEAP_FEB_29_MINUS_01_MONTH      2004-01-29
    LEAP_FEB_28_PLUS__11_MONTH      2005-01-28
    LEAP_FEB_29_PLUS__11_MONTH      2005-01-31
    LEAP_FEB_28_PLUS__12_MONTH      2005-02-28
    LEAP_FEB_29_PLUS__12_MONTH      2005-02-28
    LEAP_FEB_28_MINUS_11_MONTH      2003-03-28
    LEAP_FEB_29_MINUS_11_MONTH      2003-03-29
    LEAP_FEB_28_MINUS_12_MONTH      2003-02-28
    LEAP_FEB_29_MINUS_12_MONTH      2003-02-28
    LEAP_MAR_31_MINUS_01_MONTH      2004-02-29

    NONL_JAN_31_PLUS__01_MONTH      2003-02-28
    NONL_FEB_28_PLUS__01_MONTH      2003-03-28
    NONL_FEB_28_MINUS_01_MONTH      2003-01-28
    NONL_FEB_28_PLUS__11_MONTH      2004-01-28
    NONL_FEB_28_PLUS__12_MONTH      2004-02-28
    NONL_FEB_28_MINUS_11_MONTH      2002-03-28
    NONL_FEB_28_MINUS_12_MONTH      2002-02-28
    NONL_MAR_31_MINUS_01_MONTH      2003-02-28
 """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

