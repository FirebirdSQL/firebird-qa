#coding:utf-8
#
# id:           bugs.core_3526
# title:        Support for WHEN SQLSTATE
# decription:   
#                   Checked on:
#                        3.0.4.32939: OK, 1.266s.
#                        4.0.0.943: OK, 1.484s.
#                
# tracker_id:   CORE-3526
# min_versions: ['3.0.0']
# versions:     3.0
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
    set term ^;
    execute block returns(msg varchar(1000)) as
        declare c smallint = 32767;
    begin
        msg='';
        begin
            c = c+1;
        when SQLSTATE '22003' do
            begin
               msg = 'got exception with sqlstate = ' || sqlstate || '; ' ;
            end
        end
        suspend;
    end
    ^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MSG                             got exception with sqlstate = 22003;
  """

@pytest.mark.version('>=3.0')
def test_core_3526_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

