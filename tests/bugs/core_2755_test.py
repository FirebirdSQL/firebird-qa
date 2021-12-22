#coding:utf-8
#
# id:           bugs.core_2755
# title:        SIMILAR TO works wrongly
# decription:   
# tracker_id:   CORE-2755
# min_versions: ['2.5.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """select
    case when 'ab' SIMILAR TO 'ab|cd|efg' then 'ok' else 'bad' end as ab,
    case when 'efg' SIMILAR TO 'ab|cd|efg' then 'ok' else 'bad' end as efg,
    case when 'a' SIMILAR TO 'ab|cd|efg' then 'bad' else 'ok' end as a
  from rdb$database;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
AB     EFG    A
====== ====== ======
ok     ok     ok

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

