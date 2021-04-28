#coding:utf-8
#
# id:           bugs.core_4155
# title:        External routines DDL in Packages wrongly report error for termination with semi-colon
# decription:   
#                   Confirmed compile error on WI-T3.0.0.30566 Alpha 1, got there:
#                       Statement failed, SQLSTATE = 42000 / Dynamic SQL Error
#                       -SQL error code = -104 / -Token unknown...
#                       -;
#                   No such error in 3.0.5 and 4.0.x, but one cannot check 3.05 functionality because there is no 
#                   %FB3x_HOME%\\plugins\\udr\\udrcpp_example.dll in all 3.x snapshots since at least 3.0.0.
#                   This lead to: "Statement failed, SQLSTATE = HY000 / UDR module not loaded"
#                   Sent letter to dimitr 30.04.2019 14:01, waiting for reply.
#               
#                   Checked on 4.0.0.1501: OK, 1.621s.
#                
# tracker_id:   CORE-4155
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
    set term ^;
    create or alter package pkg
    as
    begin
        function sum_args (
            n1 integer,
            n2 integer,
            n3 integer
        ) returns integer;
    end
    ^
    recreate package body pkg
    as
    begin
        function sum_args (
            n1 integer,
            n2 integer,
            n3 integer
        ) returns integer
            external name 'udrcpp_example!sum_args'
            engine udr; -- error with the semi-colon and works without it
    end
    ^
    set term ;^
    commit;
    set list on;
    select pkg.sum_args(111,555,777) from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SUM_ARGS                        1443
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

