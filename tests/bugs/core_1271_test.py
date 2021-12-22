#coding:utf-8
#
# id:           bugs.core_1271
# title:        Ceation of invalid procedures/triggers allowed
# decription:   invalid procedures/triggers (with invalid plans, for example) was allowed to be created
# tracker_id:   CORE-1271
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1271-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create procedure p returns (out int) as
    begin
        for
            select rdb$relation_id
            from rdb$relations
            plan (rdb$relations order rdb$index_1)
            order by rdb$description
            into :out
        do
            suspend;
    end
    ^
    commit^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 2F000
    Error while parsing procedure P's BLR
    -index RDB$INDEX_1 cannot be used in the specified plan
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

