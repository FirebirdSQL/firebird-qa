#coding:utf-8
#
# id:           bugs.core_2265
# title:        Grouping by function doesn't work properly
# decription:   
# tracker_id:   CORE-2265
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """create table t (col1 date, col2 int);
commit;

insert into t values ('2011-01-01', 1);
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select extract(year from col1), sum(col2)
from t
group by extract(year from col1);

select extract(year from col1), sum(col2)
from t
group by 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
EXTRACT                   SUM
======= =====================
   2011                     1


EXTRACT                   SUM
======= =====================
   2011                     1

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

