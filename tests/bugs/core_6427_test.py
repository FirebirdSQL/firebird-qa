#coding:utf-8
#
# id:           bugs.core_6427
# title:        Whitespace as date separator causes conversion error
# decription:   
#                  NOTE: only space and TAB are allowed to usage as whitespace.
#                  Characters like chr(10) or chr(13) are not allowed:
#                      cast( '01.01.00 03:04:05.678' || ascii_char(10) as timestamp)
#                  -- leads to "Statement failed, SQLSTATE = 22009 / Invalid time zone region:"
#                  
#                  Checked on 4.0.0.2238.
#                
# tracker_id:   CORE-6427
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
    set heading off;

    select cast('01 jan	1900' as timestamp) from rdb$database;

    -- NB: max allowed length for string which is to be converted to timestamp is 130:
    select cast('01' || lpad('',120,' ') || 'jan 1900' as timestamp) from rdb$database;
    select cast('01' || lpad('',120,ascii_char(9)) || 'jan 1900' as timestamp) from rdb$database;
    select cast('01 jan' || lpad('',120,ascii_char(9)) || '1900' as timestamp) from rdb$database;

    select cast('01 jan	' || ascii_char(9) || '1900 1:1   ' as timestamp) from rdb$database;
    select cast('01 jan'|| ascii_char(9) || ascii_char(9) || '1900 1:11  ' as timestamp) from rdb$database;
    select cast('01 jan 1900 11:1'|| ascii_char(9) as timestamp) from rdb$database;
    select cast( ascii_char(9) || '01' || ascii_char(9) ||'jan 1900 11:11' || ascii_char(9) as timestamp) from rdb$database;

    select cast('01 jan 00' as timestamp) from rdb$database;
    select cast('01 jan 00 00:00' as timestamp) from rdb$database;

    select cast('01 01 1900' as timestamp) from rdb$database;
    select cast('01 01 00' as timestamp) from rdb$database;
    select cast('1' || ascii_char(9) || '1 0' as timestamp) from rdb$database;
    select cast('1 1' || ascii_char(9) || '1' as timestamp) from rdb$database;
    select cast('1 1' || ascii_char(9) || '9999' as timestamp) from rdb$database;

    select cast('01 01 2000' as timestamp) from rdb$database;
    select cast('12 01 2000' as timestamp) from rdb$database;
    -- conversion error (for unknown reason though...) select cast('13 01 2000' as timestamp) from rdb$database;

    select cast('01 01 00' || ascii_char(9) || '23:2.2' as timestamp) from rdb$database;
    select cast('01 01' || ascii_char(9) || '00' || ascii_char(9) || '3:45:5.9' as timestamp) from rdb$database;

    select cast( ascii_char(9) || '01 01 00' || ascii_char(9) || '3:4:5.678' as timestamp) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1900-01-01 00:00:00.0000
    1900-01-01 00:00:00.0000
    1900-01-01 00:00:00.0000
    1900-01-01 00:00:00.0000
    1900-01-01 01:01:00.0000
    1900-01-01 01:11:00.0000
    1900-01-01 11:01:00.0000
    1900-01-01 11:11:00.0000
    2000-01-01 00:00:00.0000
    2000-01-01 00:00:00.0000
    1900-01-01 00:00:00.0000
    2000-01-01 00:00:00.0000
    2000-01-01 00:00:00.0000
    2001-01-01 00:00:00.0000
    9999-01-01 00:00:00.0000
    2000-01-01 00:00:00.0000
    2000-12-01 00:00:00.0000
    2000-01-01 23:02:00.2000
    2000-01-01 03:45:05.9000
    2000-01-01 03:04:05.6780
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

