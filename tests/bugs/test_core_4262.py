#coding:utf-8
#
# id:           bugs.core_4262
# title:        Context parsing error with derived tables and CASE functions
# decription:   
# tracker_id:   CORE-4262
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

test_script_1 = """set planonly;
select col as col1, col as col2
from (
    select case when exists (select 1 from rdb$database ) then 1 else 0 end as col
    from rdb$relations
);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PLAN (RDB$DATABASE NATURAL)
PLAN (RDB$RELATIONS NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_core_4262_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

