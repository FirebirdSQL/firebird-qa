#coding:utf-8
#
# id:           bugs.core_4158
# title:        Regression: LIKE with escape does not work
# decription:   
# tracker_id:   CORE-4158
# min_versions: ['2.0.7']
# versions:     2.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table tab1 (
      id int constraint pk_tab1 primary key,
      val varchar(30)
    );
    
    insert into tab1 (id, val) values (1, 'abcdef');
    insert into tab1 (id, val) values (2, 'abc_ef');
    insert into tab1 (id, val) values (3, 'abc%ef');
    insert into tab1 (id, val) values (4, 'abc&%ef'); 
    insert into tab1 (id, val) values (5, 'abc&_ef');
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select id, val from tab1 where val like 'abc&%ef' escape '&';
    select id, val from tab1 where val like 'abc&_ef' escape '&';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              3
    VAL                             abc%ef
    ID                              2
    VAL                             abc_ef
  """

@pytest.mark.version('>=2.0.7')
def test_core_4158_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

