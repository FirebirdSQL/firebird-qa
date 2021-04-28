#coding:utf-8
#
# id:           bugs.core_5726
# title:        Unclear error message when inserting value exceeding max of dec_fixed decimal
# decription:   
#                   FB40SS, build 4.0.0.1008: OK, 1.641s.
#                   Previously used:
#                       create table extdecimal( dec34_34 decimal(34, 34) );
#                       insert into extdecimal values(1);
#                   -- and this raised following exception:
#                       SQLCODE: -901
#                       Decimal float invalid operation.  An indeterminant error occurred during an operation.
#                       numeric value is out of range
#                   ==================================
#                   Since 30.10.2019 DDL was changed:
#                       create table test(n numeric(38,38) );
#                       insert into test values( 1.70141183460469231731687303715884105727 ); -- must PASS
#                       insert into test values( 1.70141183460469231731687303715884105727001 ); -- must FAIL.
#                   Explanation:
#                       1.70141183460469231731687303715884105727 represents
#                       2^127-1 // 170141183460469231731687303715884105728-1
#                   
#                   Checked on:  4.0.0.1635
#                   25.06.2020, 4.0.0.2076: changed types in SQLDA from numeric to int128 // after discuss with Alex about CORE-6342.
#                
# tracker_id:   CORE-5726
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!(sqltype|max_precise_number)).)*$', ''), ('[ \t]+', ' '), ('.*alias.*', '')]

init_script_1 = """
    -- insert into test(n) values(
    -- 1.70141183460469231731687303715);
    -- insert into test(n) values(1.7014118346046923173168730371588410572700);

    recreate table test (
       id integer generated always as identity primary key,
       n numeric(38,38)
    );
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    insert into test(n) values( 1.70141183460469231731687303715884105727 );
    insert into test(n) values( 1.70141183460469231731687303715884105727001 );
    set sqlda_display on;
    select n as "max_precise_number" from test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 32752 INT128 Nullable scale: -38 subtype: 1 len: 16
    max_precise_number 1.70141183460469231731687303715884105727
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    arithmetic exception, numeric overflow, or string truncation
    -numeric value is out of range
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

