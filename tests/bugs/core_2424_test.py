#coding:utf-8

"""
ID:          issue-2840
ISSUE:       2840
TITLE:       Make CREATE VIEW infer column names for views involving a GROUP BY clause or derived table
DESCRIPTION:
JIRA:        CORE-2424
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """create view V as select d.rdb$relation_id from rdb$database d group by d.rdb$relation_id;
show view v;
recreate view V as select a from (select 1 a from rdb$database);
show view v;
"""

act = isql_act('db', test_script)

expected_stdout = """RDB$RELATION_ID                 SMALLINT Expression
View Source:
==== ======
 select d.rdb$relation_id from rdb$database d group by d.rdb$relation_id
A                               INTEGER Expression
View Source:
==== ======
 select a from (select 1 a from rdb$database)
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

