#coding:utf-8
#
# id:           bugs.core_1056
# title:        A query could produce different results, depending on the presence of an index
# decription:   
# tracker_id:   CORE-1056
# min_versions: []
# versions:     2.0
# qmid:         bugs.core_1056

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t (c varchar(10) character set win1250 collate pxw_csy);
insert into t values ('ch');
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set plan on;

select * from t where c starting with 'c';
commit;

create index t_c on t (c);
commit;

select * from t where c starting with 'c';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PLAN (T NATURAL)

C
==========
ch


PLAN (T INDEX (T_C))

C
==========
ch

"""

@pytest.mark.version('>=2.0')
def test_core_1056_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

