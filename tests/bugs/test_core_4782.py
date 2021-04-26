#coding:utf-8
#
# id:           bugs.core_4782
# title:        Command `SHOW TABLE` fails when the table contains field with unicode collationin its DDL
# decription:   
# tracker_id:   CORE-4782
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- NB: it was connection charset = UTF8 that causes error, title of ticket should be changed.
    create view v_test as select d.rdb$relation_id from rdb$database d;
    commit;
    show view v_test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$RELATION_ID                 (RDB$RELATION_ID) SMALLINT Nullable
    View Source:
    ==== ======
    select d.rdb$relation_id from rdb$database d
  """

@pytest.mark.version('>=3.0')
def test_core_4782_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

