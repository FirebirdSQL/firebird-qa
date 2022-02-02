#coding:utf-8

"""
ID:          issue-2270
ISSUE:       2270
TITLE:       Possible overflow in RDB$VIEW_RELATIONS.RDB$CONTEXT_NAME
DESCRIPTION:
  Originale tite is: If some VIEW used derived tables and long table names/aliases,
    It is possible to overflow RDB$VIEW_RELATIONS.RDB$CONTEXT_NAME
JIRA:        CORE-1841
FBTEST:      bugs.core_1841
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """create view x (id) as
select RDB$RELATION_ID
 from (select * from RDB$DATABASE long_alias_long_alias_1) long_alias_long_alias_2;
COMMIT;
SHOW VIEW x;
"""

act = isql_act('db', test_script)

expected_stdout = """ID                              SMALLINT Expression
View Source:
==== ======

select RDB$RELATION_ID
 from (select * from RDB$DATABASE long_alias_long_alias_1) long_alias_long_alias_2
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

