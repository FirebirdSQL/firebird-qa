#coding:utf-8
#
# id:           bugs.core_6328
# title:        FB4 Beta 2 may still be using the current date for TIME WITH TIME ZONE and extended wire protocol.
# decription:   
#                   Confirmed bug on 4.0.0.2104 (got TZ_HOUR = -4 instead of expected -5).
#                   Checked on 4.0.0.2108 (intermediate build of 17.07.2020 16:34) - works fine.
#                
# tracker_id:   CORE-6328
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bind of time zone to extended;
    create table test (
        timecol time with time zone
    );

    insert into test(timecol) values('11:31:05.0001 america/new_york');

    set list on;
    select extract(timezone_hour from timecol) as tz_hour, extract(timezone_minute from timecol) as tz_minute
    from test;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TZ_HOUR                         -5
    TZ_MINUTE                       0
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

