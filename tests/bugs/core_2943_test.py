#coding:utf-8
#
# id:           bugs.core_2943
# title:        parsing error recursive query with two recursive parts
# decription:   
# tracker_id:   CORE-2943
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    with recursive
    tree (NAME) as (
      select r.rdb$relation_name from rdb$relations r
      union all
      select r2.rdb$relation_name || tree.NAME from rdb$relations r2, tree
      where 1 = 0
    ),
    tree_2 as (
        select c.rdb$character_set_name from rdb$character_sets c
        union all
        select c2.rdb$character_set_name from rdb$character_sets c2, tree_2
        where 1 = 0
    )
    select * from tree, tree_2 where NAME=upper('RDB$PAGES') and RDB$CHARACTER_SET_NAME=upper('NONE');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    NAME                            RDB$PAGES
    RDB$CHARACTER_SET_NAME          NONE
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

