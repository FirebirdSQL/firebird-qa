#coding:utf-8
#
# id:           bugs.core_4149
# title:        New permission types are not displayed by ISQL
# decription:
# tracker_id:   CORE-4149
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(id int);
    commit;
    grant select on test to public;
    commit;
    show grants;

    create sequence g_test;
    commit;

    grant usage on sequence g_test to public;
    commit;
    show grants;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
/* Grant permissions for this database */
GRANT SELECT ON TEST TO PUBLIC
GRANT CREATE DATABASE TO USER TMP$C4648

/* Grant permissions for this database */
GRANT SELECT ON TEST TO PUBLIC
GRANT USAGE ON SEQUENCE G_TEST TO PUBLIC
GRANT CREATE DATABASE TO USER TMP$C4648
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

