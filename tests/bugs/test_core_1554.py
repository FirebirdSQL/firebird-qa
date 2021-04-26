#coding:utf-8
#
# id:           bugs.core_1554
# title:        select ... where ... <> ALL (select ... join ...) bug
# decription:   
# tracker_id:   
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         bugs.core_1554

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select
    (
        select count(*) from rdb$triggers t1
    )
    -
    (
        select count(*)
        from rdb$triggers t1
        where
            t1.RDB$SYSTEM_FLAG=1 and
            t1.rdb$trigger_name <>
            all (
                select t2.rdb$trigger_name
                from rdb$triggers t2
                join rdb$triggers t3 on t3.rdb$trigger_name=t2.rdb$trigger_name
                where t2.rdb$trigger_name='xxx'
            )
    ) as cnt
    from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNT                             0
  """

@pytest.mark.version('>=2.1.7')
def test_core_1554_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

