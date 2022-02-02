#coding:utf-8

"""
ID:          issue-2630
ISSUE:       2630
TITLE:       RDB$VIEW_RELATIONS is not cleaned when altering a view
DESCRIPTION:
JIRA:        CORE-2202
FBTEST:      bugs.core_2202
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table table_1 (id integer);
    recreate table table_2 (id integer);
    recreate table table_3 (id integer);

    create or alter view vw_table(id) as
    select id from table_1;
    commit;

    create or alter view vw_table(id) as
    select id from table_2;
    commit;

    create or alter view vw_table(id) as
    select id
    from table_3;
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set list on;
    set width vew_name 31;
    set width rel_name 31;
    set width ctx_name 31;
    select
         rdb$view_name as vew_name
        ,rdb$relation_name as rel_name
        ,rdb$view_context
        ,rdb$context_name as ctx_name
    from rdb$view_relations rv;
"""

act = isql_act('db', test_script)

expected_stdout = """
    VEW_NAME                        VW_TABLE
    REL_NAME                        TABLE_3
    RDB$VIEW_CONTEXT                1
    CTX_NAME                        TABLE_3
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

