#coding:utf-8
#
# id:           bugs.core_2756
# title:        substring from timestamp - unexpected result
# decription:   
#                   26.01.2019. Note for 4.0.
#                   Made more careful parsing for each token of timestamp because of time-with-timezone introduction.
#                   Checed on:
#                       4.0.0.1340: OK, 2.313s.
#                       4.0.0.1410: OK, 2.360s.
#               
#                   02.02.2019. Note for 4.0.
#                   One need to EXPLICITLY add statement SET TIME ZONE <+HH:MM> at the beginning of test, otherwise
#                   we will get eception because current_timestamp string will have length more than expected.
#                   This is because DEFAULT time zone in FB 4.0 includes REGION NAME ('Moscow/Europe") instead of HH:MM shift.
#                   Checked on:
#                       4.0.0.1421: OK, 1.493s.
#               
#                
# tracker_id:   CORE-2756
# min_versions: ['2.5.1']
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
    set list on;
    set time zone '+00:00';

    select
         -- dts,
         iif( left(dts,4) = extract(year from current_timestamp), 'Looks as expected', 'Unexpected for dts = ' || dts ) as year_as_numeric
        ,iif( substring(dts from  5 for 1) = '-', 'Looks as expected', 'Unexpected for dts = ' || dts) as year_month_separator
        ,iif( substring(dts from  6 for 2) = lpad(extract(month from current_timestamp),2,'0'), 'Looks as expected', 'Unexpected for dts = ' || dts ) month_as_numeric
        ,iif( substring(dts from  8 for 1) = '-', 'Looks as expected', 'Unexpected for dts = ' || dts) as month_day_separator
        ,iif( substring(dts from  9 for 2) = lpad(extract(day from current_timestamp),2,'0'), 'Looks as expected', 'Unexpected for dts = ' || dts ) day_as_numeric
        ,iif( substring(dts from 11 for 1) = ' ', 'Looks as expected', 'Unexpected for dts = ' || dts) as date_time_space_separator
        ,iif( substring(dts from 12 for 2) = lpad(extract(hour from current_timestamp),2,'0'), 'Looks as expected', 'Unexpected for dts = ' || dts ) hour_as_numeric
        ,iif( substring(dts from 14 for 1) = ':', 'Looks as expected', 'Unexpected for dts = ' || dts) as time_hours_minutes_separator
        ,iif( substring(dts from 15 for 2) = lpad(extract(minute from current_timestamp),2,'0'), 'Looks as expected', 'Unexpected for dts = ' || dts ) minute_as_numeric
        ,iif( substring(dts from 17 for 1) = ':', 'Looks as expected', 'Unexpected for dts = ' || dts) as time_minutes_seconds_separator
        ,iif( substring(dts from 18 for 2) = lpad( floor(extract(second from current_timestamp)), 2,'0'), 'Looks as expected', 'Unexpected for dts = ' || dts ) second_as_numeric
        ,iif( substring(dts from 20 for 1) = '.', 'Looks as expected', 'Unexpected for dts = ' || dts) as time_seconds_millis_separator
        ,iif( substring(dts from 21 for 4) = lpad( 10 * floor(extract( millisecond from current_timestamp)),4,'0'), 'Looks as expected', 'Unexpected for dts = ' || dts ) millisec_as_numeric
        ,iif( substring(dts from 25 for 1) = ' ', 'Looks as expected', 'Unexpected for dts = ' || dts) as time_timezone_space_separator
        ,iif( substring(dts from 26 for 1) in ('+','-'), 'Looks as expected', 'Unexpected for dts = ' || dts) GMT_shift_direction
        ,iif( substring(dts from 27 for 2) similar to '[[:DIGIT:]]{2}', 'Looks as expected', 'Unexpected for dts = ' || dts) GMT_shift_hours
        ,iif( substring(dts from 29 for 1) = ':', 'Looks as expected', 'Unexpected for dts = ' || dts) as GMT_shift_time_separator
        ,iif( substring(dts from 30 for 2) similar to '[[:DIGIT:]]{2}', 'Looks as expected', 'Unexpected for dts = ' || dts) GMT_shift_minutes
    from (
        select
        substring(current_timestamp from 1 for 31) dts
        from rdb$database
    ) x;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    YEAR_AS_NUMERIC                 Looks as expected
    YEAR_MONTH_SEPARATOR            Looks as expected
    MONTH_AS_NUMERIC                Looks as expected
    MONTH_DAY_SEPARATOR             Looks as expected
    DAY_AS_NUMERIC                  Looks as expected
    DATE_TIME_SPACE_SEPARATOR       Looks as expected
    HOUR_AS_NUMERIC                 Looks as expected
    TIME_HOURS_MINUTES_SEPARATOR    Looks as expected
    MINUTE_AS_NUMERIC               Looks as expected
    TIME_MINUTES_SECONDS_SEPARATOR  Looks as expected
    SECOND_AS_NUMERIC               Looks as expected
    TIME_SECONDS_MILLIS_SEPARATOR   Looks as expected
    MILLISEC_AS_NUMERIC             Looks as expected
    TIME_TIMEZONE_SPACE_SEPARATOR   Looks as expected
    GMT_SHIFT_DIRECTION             Looks as expected
    GMT_SHIFT_HOURS                 Looks as expected
    GMT_SHIFT_TIME_SEPARATOR        Looks as expected
    GMT_SHIFT_MINUTES               Looks as expected
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

