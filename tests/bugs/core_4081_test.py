#coding:utf-8
#
# id:           bugs.core_4081
# title:        Regression: Built-in functions and subselect no longer supported in "update or insert" value list
# decription:   
# tracker_id:   CORE-4081
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table test (uid varchar(64));
    commit;

    update or insert into test (uid) values ( uuid_to_char(gen_uuid()) )
    matching (uid);

    update or insert into test (uid)
    values ( (select uuid_to_char(gen_uuid()) from rdb$database) )
    matching (uid);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

