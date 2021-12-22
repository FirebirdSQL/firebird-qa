#coding:utf-8
#
# id:           bugs.core_3374
# title:        Server may crash or corrupt data if SELECT WITH LOCK is issued against records not in the latest format
# decription:   Actually there is NO crash in 2.5.0, checked SS/SC/CS, WI-V2.5.0.26074.
# tracker_id:   CORE-3374
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table test (col1 int, col2 varchar(10), col3 date);
    insert into test values (1, 'qwerty', date '01.01.2015');
    alter table test drop col2;
    set list on;
    select * from test order by col1 with lock; -- crash here 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    COL1                            1
    COL3                            2015-01-01
"""

@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

