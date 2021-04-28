#coding:utf-8
#
# id:           bugs.core_5684
# title:        Error "no current record for fetch operation" is raised while deleting record from MON$ATTACHMENTS using ORDER BY clause
# decription:   
#                   Checked on:
#                       2.5.8.27088: OK, 1.344s.
#                       3.0.3.32856: OK, 1.453s.
#                       4.0.0.834: OK, 1.750s.
#                
# tracker_id:   CORE-5684
# min_versions: ['2.5.8']
# versions:     2.5.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    commit; 
    set count on;
    delete from mon$attachments order by mon$attachment_id rows 1; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 1
  """

@pytest.mark.version('>=2.5.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

