#coding:utf-8
#
# id:           bugs.core_4118
# title:        Expression index may be not used for derived fields or view fields
# decription:   
# tracker_id:   CORE-4118
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """create table t (id int, d timestamp);
create index itd on t computed (cast(d as date));
COMMIT;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
select * from t where cast(d as date) = current_date;
select * from (select id, cast(d as date) as d from t) where d = current_date;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """SQL>
PLAN (T INDEX (ITD))
SQL>
PLAN (T INDEX (ITD))
SQL>"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

