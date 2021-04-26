#coding:utf-8
#
# id:           bugs.core_3330
# title:        Server crashes while recreating the table with a NULL -> NOT NULL change
# decription:   
# tracker_id:   CORE-3330
# min_versions: ['3.0']
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
    create table test (a int);
    commit;
    insert into test (a) values (null);
    commit;
    recreate table test (b int not null);
    commit; -- crash here 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_3330_1(act_1: Action):
    act_1.execute()

