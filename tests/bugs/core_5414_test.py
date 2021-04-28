#coding:utf-8
#
# id:           bugs.core_5414
# title:        Error restoring on FB 3.0 from FB 2.5: bugcheck 221 (cannot remap)
# decription:   
#                   Test verifies only issue 08/Dec/16 02:47 PM (pointed out by ASF).
#                   Confirmed bug on 3.0.1.32539, 3.0.2.32643 got on new database:
#                       SQL> select 1 from rdb$database a full join rdb$database b on (exists(select 1 from rdb$database));
#                       Statement failed, SQLSTATE = XX000
#                       internal Firebird consistency check ((CMP) copy: cannot remap (221), file: RecordSourceNodes.cpp line: 594)
#                   Checked on 3.0.2.32676, 4.0.0.511 -- all fine.
#                
# tracker_id:   CORE-5414
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on; 
    select 1 x from rdb$database a full join rdb$database b on (exists(select 1 from rdb$database));
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    X                               1
  """

@pytest.mark.version('>=3.0.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

