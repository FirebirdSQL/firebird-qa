#coding:utf-8
#
# id:           bugs.core_4084
# title:        Regression: Group by fails if subselect-column is involved
# decription:   
# tracker_id:   CORE-4084
# min_versions: ['2.0']
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
    set planonly;
    select
        iif(d is null, 10, 0) + sys as sys,
        count(*)
    from (
        select
            ( select d.rdb$relation_id from rdb$database d ) as d,
            coalesce(r.rdb$system_flag, 0) as sys
        from rdb$relations r
    )
    group by 1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (D NATURAL)
    PLAN SORT (R NATURAL)
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

