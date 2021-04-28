#coding:utf-8
#
# id:           bugs.core_4350
# title:        Support the SQL Standard ALTER SEQUENCE .. RESTART (without WITH clause)
# decription:   
#                   :::::::::::::::::::::::::::::::::::::::: NB ::::::::::::::::::::::::::::::::::::
#                   18.08.2020. FB 4.x has incompatible behaviour with all previous versions since build 4.0.0.2131 (06-aug-2020):
#                   statement 'alter sequence <seq_name> restart with 0' changes rdb$generators.rdb$initial_value to -1 thus next call
#                   gen_id(<seq_name>,1) will return 0 (ZERO!) rather than 1. 
#                   See also CORE-6084 and its fix: https://github.com/FirebirdSQL/firebird/commit/23dc0c6297825b2e9006f4d5a2c488702091033d
#                   ::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#                   This is considered as *expected* and is noted in doc/README.incompatibilities.3to4.txt
#               
#                   Because of this, it was decided to make separate section for check results of FB 4.x
#                   Checked on 4.0.0.2164, 3.0.7.33356
#                 
# tracker_id:   CORE-4350
# min_versions: ['3.0']
# versions:     3.0, 4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate sequence g1 start with 9223372036854775807 increment by -2147483647;
    recreate sequence g2 start with -9223372036854775808 increment by 2147483647;
    recreate sequence g3 start with 9223372036854775807 increment by  2147483647;
    recreate sequence g4 start with -9223372036854775808 increment by -2147483647;
    commit;
    set list on;
    select next value for g1, next value for g2, next value for g3, next value for g4
    from rdb$database;
    
    alter sequence g1 restart;
    alter sequence g2 restart;
    alter sequence g3 restart;
    alter sequence g4 restart;
    commit;
    
    show sequ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    NEXT_VALUE                      9223372034707292160
    NEXT_VALUE                      -9223372034707292161
    NEXT_VALUE                      -9223372034707292162
    NEXT_VALUE                      9223372034707292161
    
    Generator G1, current value: 9223372036854775807, initial value: 9223372036854775807, increment: -2147483647
    Generator G2, current value: -9223372036854775808, initial value: -9223372036854775808, increment: 2147483647
    Generator G3, current value: 9223372036854775807, initial value: 9223372036854775807, increment: 2147483647
    Generator G4, current value: -9223372036854775808, initial value: -9223372036854775808, increment: -2147483647
  """

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

# version: 4.0
# resources: None

substitutions_2 = [('=.*', ''), ('[ \t]+', ' ')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

test_script_2 = """
    recreate sequence g1 start with 9223372036854775807 increment by -2147483647;
    recreate sequence g2 start with -9223372036854775808 increment by 2147483647;
    recreate sequence g3 start with 9223372036854775807 increment by  2147483647;
    recreate sequence g4 start with -9223372036854775808 increment by -2147483647;
    commit;
    set list on;
    select next value for g1, next value for g2, next value for g3, next value for g4
    from rdb$database;
    
    alter sequence g1 restart;
    alter sequence g2 restart;
    alter sequence g3 restart;
    alter sequence g4 restart;
    commit;
    
    show sequ;
  """

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    NEXT_VALUE                      9223372036854775807
    NEXT_VALUE                      -9223372036854775808
    NEXT_VALUE                      9223372036854775807
    NEXT_VALUE                      -9223372036854775808
    Generator G1, current value: -9223372034707292162, initial value: 9223372036854775807, increment: -2147483647
    Generator G2, current value: 9223372034707292161, initial value: -9223372036854775808, increment: 2147483647
    Generator G3, current value: 9223372034707292160, initial value: 9223372036854775807, increment: 2147483647
    Generator G4, current value: -9223372034707292161, initial value: -9223372036854775808, increment: -2147483647
  """

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

