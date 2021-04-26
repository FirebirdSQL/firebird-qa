#coding:utf-8
#
# id:           bugs.core_1724
# title:        Common table expressions cannot be used in computed columns and quantified predicates (IN / ANY / ALL)
# decription:   
# tracker_id:   CORE-1724
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
    set list on;
    select
        sign( count(*) ) +
        (
          with recursive
          n as(
            select 0 i from rdb$database
            union all
            select n.i+1 from n
            where n.i < 10
          )
          select avg(i)
          from n
        ) s
    from rdb$pages p
    where p.rdb$relation_id
    > all (
        with recursive
        n as(
          select 0 i from rdb$database
          union all
          select n.i+1 from n
          where n.i < 10
        )
        select i
        from n
    )
    and p.rdb$page_number
    not in (
        with recursive
        n as(
          select 0 i from rdb$database
          union all
          select n.i+1 from n
          where n.i < 10
        )
        select i
        from n
    );
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    S                               6
  """

@pytest.mark.version('>=2.5')
def test_core_1724_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

