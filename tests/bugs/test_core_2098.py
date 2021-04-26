#coding:utf-8
#
# id:           bugs.core_2098
# title:        View over global temporary table
# decription:   
# tracker_id:   CORE-2098
# min_versions: []
# versions:     2.1.2
# qmid:         bugs.core_2098

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.2
# resources: None

substitutions_1 = []

init_script_1 = """create global temporary table temptable (
 id integer);
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """recreate view tempview1
as
select
 a.id as id
from
 temptable a;
commit;
recreate view tempview2
as
select
 a.id + 1 as id
from
 temptable a;
commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1.2')
def test_core_2098_1(act_1: Action):
    act_1.execute()

