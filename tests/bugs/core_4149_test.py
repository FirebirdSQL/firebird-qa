#coding:utf-8

"""
ID:          issue-4476
ISSUE:       4476
TITLE:       New permission types are not displayed by ISQL
DESCRIPTION:
JIRA:        CORE-4149
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test(id int);
    commit;
    grant select on test to public;
    commit;
    show grants;

    create sequence g_test;
    commit;

    grant usage on sequence g_test to public;
    commit;
    show grants;
"""

act = isql_act('db', test_script)

expected_stdout = """
/* Grant permissions for this database */
GRANT SELECT ON TEST TO PUBLIC

/* Grant permissions for this database */
GRANT SELECT ON TEST TO PUBLIC
GRANT USAGE ON SEQUENCE G_TEST TO PUBLIC
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

