#coding:utf-8
#
# id:           bugs.core_6385
# title:        Wrong line and column information after IF statement
# decription:   
#                   DO NOT make indentation or excessive empty lines in the code that is executed by ISQL.
#                   Checked on 4.0.0.2170.
#                 
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!At\\s+block\\s+line).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
set term ^;
execute block
as
    declare n integer;
begin
    if (1 = 1) then
        n = 1;
    n = n / 0;
end^
set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
-At block line: 7, col: 5
  """

@pytest.mark.version('>=4.0')
def test_core_6385_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

