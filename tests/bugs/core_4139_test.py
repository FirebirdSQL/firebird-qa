#coding:utf-8
#
# id:           bugs.core_4139
# title:         Error "invalid stream" can be raised in some cases while matching a computed index
# decription:   
# tracker_id:   CORE-4139
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """create table A (ID int);
create table B (ID int);
create index IDX on A computed by (ID);
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SET HEADING OFF;
select min( (select 1 from A where cast(ID as int) = B.ID) ) from B;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """<null>"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

