#coding:utf-8
#
# id:           bugs.core_2916
# title:        Broken error handling in the case of a conversion error happened during index creation
# decription:   
# tracker_id:   CORE-2916
# min_versions: ['2.1.4']
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
    recreate table tab (col date);
    insert into tab (col) values ( date '29.02.2004' );
    commit;

    create index itab on tab computed (cast(col as int));
    commit;
    set list on;
    select * from tab where cast(col as int) is null;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22018
    Expression evaluation error for index "***unknown***" on table "TAB"
    -conversion error from string "2004-02-29"
    Statement failed, SQLSTATE = 22018
    conversion error from string "2004-02-29"
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

