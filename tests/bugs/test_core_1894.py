#coding:utf-8
#
# id:           bugs.core_1894
# title:        Circular dependencies between computed fields crashs the engine
# decription:   
#                  Checked on LI-T4.0.0.419 after commit 19.10.2016 18:26
#                  https://github.com/FirebirdSQL/firebird/commit/6a00b3aee6ba17b2f80a5b00def728023e347707
#                  -- all OK.
#                
# tracker_id:   CORE-1894
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
    recreate table t (
        n integer,
        n1 computed by (n),
        n2 computed by (n1)
    );

    recreate table t2 (
        n integer,
        c1 computed by (1),
        c2 computed by (c1)
    );

    alter table t alter n1 computed by (n2);
    commit;

    set autoddl off;
    alter table t2 drop c1;
    alter table t2 add c1 computed by (c2);
    commit;

    select * from t;
    select * from t2; -- THIS LEAD SERVER CRASH (checked on WI-T4.0.0.399)

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -Cannot have circular dependencies with computed fields

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN T2.C1
    -there are 1 dependencies

    Statement failed, SQLSTATE = 42000
    Cannot have circular dependencies with computed fields

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -COLUMN T2.C1
    -there are 1 dependencies
  """

@pytest.mark.version('>=3.0.2')
def test_core_1894_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

