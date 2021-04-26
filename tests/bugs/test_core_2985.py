#coding:utf-8
#
# id:           bugs.core_2985
# title:        The new 2.5 feature to alter COMPUTED columns doesn't handle dependencies well
# decription:   
# tracker_id:   CORE-2985
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table test (id numeric, f1 varchar(20));
create table test1(id1 numeric, ff computed((select f1 from test where id=id1)));
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """show table test1;
alter table test1 alter ff computed(cast(null as varchar(20)));
drop table test;
commit;
show table test1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """ID1                             NUMERIC(9, 0) Nullable
FF                              Computed by: ((select f1 from test where id=id1))
ID1                             NUMERIC(9, 0) Nullable
FF                              Computed by: (cast(null as varchar(20)))
"""

@pytest.mark.version('>=2.5.0')
def test_core_2985_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

