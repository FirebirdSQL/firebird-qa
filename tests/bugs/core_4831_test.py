#coding:utf-8
#
# id:           bugs.core_4831
# title:        Revoke all on all from role <R> -- failed with "SQL role <R> does not exist in security database"
# decription:
# tracker_id:   CORE-4831
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action, role_factory, Role

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    -- create role r_20150608_20h03m;
    -- commit;
    revoke all on all from role r_20150608_20h03m; -- this was failed, possibly due to: http://sourceforge.net/p/firebird/code/61729
    commit;
    show grants;
    -- commit;
    -- drop role r_20150608_20h03m;
    --commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

role_1 = role_factory('db_1', name='r_20150608_20h03m')

expected_stderr_1 = """
There is no privilege granted in this database
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, role_1: Role):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
    assert act_1.clean_stderr == act_1.clean_expected_stderr
