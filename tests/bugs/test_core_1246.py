#coding:utf-8
#
# id:           bugs.core_1246
# title:        Incorrect column values with outer joins and derived tables
# decription:   
# tracker_id:   CORE-1246
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T1 (N INTEGER);
CREATE TABLE T2 (N INTEGER);

insert into t1 values (1);
insert into t1 values (2);
insert into t2 values (2);
commit;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select *
    from (select 1 n from rdb$database) t1
    full join (select 2 n from rdb$database) t2
        on (t2.n = t1.n)
;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           N            N
============ ============
      <null>            2
           1       <null>

"""

@pytest.mark.version('>=2.5.0')
def test_core_1246_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

