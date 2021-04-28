#coding:utf-8
#
# id:           bugs.core_3722
# title:        IS NOT DISTINCT FROM NULL doesn't use index
# decription:   
# tracker_id:   CORE-3722
# min_versions: ['2.1.5']
# versions:     2.1.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.5
# resources: None

substitutions_1 = []

init_script_1 = """create table t (a varchar(5));
create index t_a on t (a);
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
select * from t where a is null;
select * from t where a is not distinct from null;
select * from t where a is not distinct from null PLAN (T INDEX (T_A));
select * from t where a is not distinct from nullif('', '');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btestnew	mpugs.core_3722.fdb, User: SYSDBA
SQL> SQL>
PLAN (T INDEX (T_A))
SQL>
PLAN (T INDEX (T_A))
SQL>
PLAN (T INDEX (T_A))
SQL>
PLAN (T INDEX (T_A))
SQL>"""

@pytest.mark.version('>=2.1.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

