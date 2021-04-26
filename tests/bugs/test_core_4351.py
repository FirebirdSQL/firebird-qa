#coding:utf-8
#
# id:           bugs.core_4351
# title:        Incorrect default value when adding a new column
# decription:   
# tracker_id:   CORE-4351
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(id int);
    commit;
    insert into test values(1);
    commit;
    alter table test add pwd varchar(50) character set utf8 default 'MdX8fLruCUQ=' not null collate utf8;
    commit;
    set list on;
    select * from test;
    -- WI-V2.1.7.18553: pwd = 'MdX'
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              1
    PWD                             MdX8fLruCUQ=
  """

@pytest.mark.version('>=2.5')
def test_core_4351_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

