#coding:utf-8

"""
ID:          issue-2727
ISSUE:       2727
TITLE:       Include PLAN in mon$statements
DESCRIPTION:
JIRA:        CORE-2303
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set blob all;
    set list on;
    commit;
    select
        (select sign(count(*)) from rdb$relations r)
       ,s.mon$explained_plan as mon_explained_blob_id
    from mon$statements s
    where
    s.mon$transaction_id = current_transaction
    and s.mon$sql_text containing 'from mon$statements' -- prevent from RDB$AUTH record, 4.0 Classic
    ;
"""

act = isql_act('db', test_script, substitutions=[('MON_EXPLAINED_BLOB_ID .*', '')])

expected_stdout = """
    SIGN                            1

    Select Expression
        -> Singularity Check
            -> Aggregate
                -> Table "RDB$RELATIONS" as "R" Full Scan
    Select Expression
        -> Filter
            -> Table "MON$STATEMENTS" as "S" Full Scan
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

