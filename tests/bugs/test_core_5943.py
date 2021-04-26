#coding:utf-8
#
# id:           bugs.core_5943
# title:        Server crashes preparing a query with both DISTINCT/ORDER BY and non-field expression in the select list
# decription:   
#                   We run query from ticket and check that it does completed OK with issuing data and 'Records affected: 1'.
#                   Confirmed bug on: 3.0.4.33053, 4.0.0.1172
#                   Works fine on:
#                       2.5.9.27119: OK, 0.468s.
#                       3.0.5.33084: OK, 1.484s.
#                       4.0.0.1249: OK, 2.453s.
#                
# tracker_id:   CORE-5943
# min_versions: ['2.5.9']
# versions:     2.5.9
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.9
# resources: None

substitutions_1 = [('F02\\s+\\d+', 'F02')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    select distinct 
        '0' as f01
       ,a.mon$server_pid as f02
    from mon$attachments a
    order by a.mon$server_pid, a.mon$server_pid
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F01                             0
    F02                             2344
    Records affected: 1
  """

@pytest.mark.version('>=2.5.9')
def test_core_5943_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

