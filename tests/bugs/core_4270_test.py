#coding:utf-8
#
# id:           bugs.core_4270
# title:        Error in case of subquery with windowed function + where <field> IN(select ...)
# decription:   
# tracker_id:   CORE-4270
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t0(q int); commit;
    create index t0_q on t0(q);
    commit;
    insert into t0(q) values (1);
    commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select a.qx
    from
    (
     select qx
     from
     (
         select 1 qx
               ,count(*)over() as c
         from t0
         where t0.q in (select 1 from rdb$database)
     ) r
    ) a
    join t0 b on a.qx = b.q;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
  QX                              1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

