#coding:utf-8
#
# id:           bugs.core_1846
# title:        Allow index walk (ORDER plan) when there is a composite index {A, B} and the query looks like WHERE A = ? ORDER BY B
# decription:   
# tracker_id:   CORE-1846
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(
       n1 int
      ,n2 int
    );
    commit;
    
    insert into test select rand()*100, rand()*100 from rdb$types;
    commit;
    
    create index test_n1_n2_asc on test(n1, n2);
    commit;
    create descending index test_n2_n1_desc on test(n2, n1);
    commit;
    
    set planonly;
    select * from test where n1 = ? order by n2 asc;
    select * from test where n2 = ? order by n1 desc;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (TEST ORDER TEST_N1_N2_ASC)
    PLAN (TEST ORDER TEST_N2_N1_DESC)
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

