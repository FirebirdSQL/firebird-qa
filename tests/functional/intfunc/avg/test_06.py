#coding:utf-8
#
# id:           functional.intfunc.avg_06
# title:        AVG - Integer OverFlow
# decription:   
#                   Refactored 14.10.2019: adjusted expected_stdout/stderr
#                   25.06.2020, 4.0.0.2076: changed types in SQLDA from numeric to int128 // after discuss with Alex about CORE-6342.
#                   09.07.2020, 4.0.0.2091:
#                       NO more overflow since INT128 was introduced. AVG() is evaluated successfully.
#                       Removed error message from expected_stderr, added result into expected_stdout.
#                
# tracker_id:   
# min_versions: []
# versions:     3.0, 4.0
# qmid:         functional.intfunc.avg.avg_06

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """
    recreate table test( id integer not null);
    insert into test values(2100000000);
    insert into test values(2100000000);
    insert into test values(2100000000);
    insert into test values(2100000000);
    commit;
    create or alter view v_test as select avg(2100000000*id)as avg_result from test;
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set sqlda_display on;
    select * from v_test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 0
    OUTPUT message field count: 1
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    : name: AVG_RESULT alias: AVG_RESULT
    : table: V_TEST owner: SYSDBA
   """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    Integer overflow.  The result of an integer operation caused the most significant bit of the result to carry.
   """

@pytest.mark.version('>=3.0,<4.0')
def test_avg_06_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('^((?!sqltype|AVG_RESULT).)*$', ''), ('[ \t]+', ' ')]

init_script_2 = """
    recreate table test( id integer not null);
    insert into test values(2100000000);
    insert into test values(2100000000);
    insert into test values(2100000000);
    insert into test values(2100000000);
    commit;
    create or alter view v_test as select avg(2100000000*id)as avg_result from test;
    commit;
  """

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    set list on;
    set sqlda_display on;
    select * from v_test;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    01: sqltype: 32752 INT128 Nullable scale: 0 subtype: 0 len: 16
      :  name: AVG_RESULT  alias: AVG_RESULT
      : table: V_TEST  owner: SYSDBA

    AVG_RESULT                                                4410000000000000000    
   """

@pytest.mark.version('>=4.0')
def test_avg_06_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

