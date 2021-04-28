#coding:utf-8
#
# id:           bugs.core_1891
# title:        SHOW VIEW shows non-sense information for view fields with expressions
# decription:   
# tracker_id:   CORE-1891
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table test (n integer);
create view view_test (x, y) as select n, n * 2 from test;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """show view view_test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """X                               INTEGER Nullable
Y                               BIGINT Expression
View Source:
==== ======
 select n, n * 2 from test
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

