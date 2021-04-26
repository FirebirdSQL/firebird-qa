#coding:utf-8
#
# id:           bugs.core_1782
# title:        ISQL crashes when fetching data for a column having alias longer than 30 characters
# decription:   
# tracker_id:   CORE-1782
# min_versions: ['2.1.7']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select 1 as test567890test567890test567890test567890 from rdb$database; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Name longer than database column size
  """

@pytest.mark.version('>=3.0,<4.0')
def test_core_1782_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

# version: 4.0
# resources: None

substitutions_2 = [('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+', '')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    -- NB: 4.0 has limit on length of column size = 255 _bytes_ (not characters).
    -- More complex test see in core_2350.fbt
    set list on;
select 'Check column title, ASCII, width = 256' as 
i2345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890i2345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890i23456789012345678901234567890123456
from rdb$database;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stderr_2 = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -token size exceeds limit
  """

@pytest.mark.version('>=4.0')
def test_core_1782_2(act_2: Action):
    act_2.expected_stderr = expected_stderr_2
    act_2.execute()
    assert act_2.clean_expected_stderr == act_2.clean_stderr

