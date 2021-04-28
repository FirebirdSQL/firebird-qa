#coding:utf-8
#
# id:           bugs.core_3806
# title:        Wrong data returned if a sub-query or a computed field refers to the base table in the ORDER BY clause
# decription:   
# tracker_id:   CORE-3806
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """create table t (col1 int, col2 int, col3 int);
insert into t values (100, 200, 300);
insert into t values (101, 201, 301);
insert into t values (102, 202, 302);
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """alter table t drop col1;
select col2, col3 from t as t1;
select col2, col3 from t as t1 where exists (select * from t as t2 order by t1.col2 );
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """SQL>
        COL2         COL3
============ ============
         200          300
         201          301
         202          302

SQL>
        COL2         COL3
============ ============
         200          300
         201          301
         202          302

SQL>"""

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

