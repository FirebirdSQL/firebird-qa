#coding:utf-8
#
# id:           bugs.core_6286
# title:        Make usage of TIMESTAMP/TIME WITH TIME ZONE convenient for users when appropriate ICU library is not installed on the client side
# decription:   
#                   Test only verifies ability to use 'EXTENDED' clause in SET BIND statement.
#                   We can not simulate absense of appropriate ICU library and for this reason values of time/timestamp are suppressednot checked.
#                   Checked on 4.0.0.1905.
#                
# tracker_id:   CORE-6286
# min_versions: []
# versions:     4.0.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.0
# resources: None

substitutions_1 = [('^((?!(sqltype|extended)).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;

    set bind of time with time zone to extended;
    select time '11:11:11.111 Indian/Cocos' as "check_bind_time_with_zone_to_extended" from rdb$database;

    set bind of timestamp with time zone to extended;
    select timestamp '2018-12-31 12:31:42.543 Pacific/Fiji' as "check_bind_timestamp_with_zone_to_extended" from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 32750 EXTENDED TIME WITH TIME ZONE scale: 0 subtype: 0 len: 8
      :  name: CONSTANT  alias: check_bind_time_with_zone_to_extended
    check_bind_time_with_zone_to_extended

    01: sqltype: 32748 EXTENDED TIMESTAMP WITH TIME ZONE scale: 0 subtype: 0 len: 12
      :  name: CONSTANT  alias: check_bind_timestamp_with_zone_to_extended
    check_bind_timestamp_with_zone_to_extended
  """

@pytest.mark.version('>=4.0.0')
def test_core_6286_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

