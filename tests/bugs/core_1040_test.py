#coding:utf-8
#
# id:           bugs.core_1040
# title:        Wrong single-segment ascending index on character field with NULL and empty string values
# decription:   Wrong single-segment ascending index on character field with NULL and empty string values
# tracker_id:   CORE-1040
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1040

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """recreate table t (str varchar(10));
commit;

insert into t values ('');
insert into t values (null);
commit;

create index t_i on t (str);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select count(*) from t where str is null;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                COUNT
=====================
                    1

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

