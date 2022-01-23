#coding:utf-8

"""
ID:          issue-4530
ISSUE:       4530
TITLE:       ISQL -x does not output the START WITH clause of generators/sequences
DESCRIPTION:
JIRA:        CORE-4205
"""

import pytest
from firebird.qa import *

init_script = """
    recreate sequence tmp_gen_42051 start with 9223372036854775807 increment by -2147483647;
    recreate sequence tmp_gen_42052 start with -9223372036854775808 increment by 2147483647;
    recreate sequence tmp_gen_42053 start with 9223372036854775807 increment by  2147483647;
    recreate sequence tmp_gen_42054 start with -9223372036854775808 increment by -2147483647;
"""

db = db_factory(sql_dialect=3, init=init_script)

act = python_act('db', substitutions=[('^((?!CREATE GENERATOR).)*$', '')])

expected_stdout = """
    CREATE GENERATOR TMP_GEN_42051 START WITH 9223372036854775807 INCREMENT -2147483647;
    CREATE GENERATOR TMP_GEN_42052 START WITH -9223372036854775808 INCREMENT 2147483647;
    CREATE GENERATOR TMP_GEN_42053 START WITH 9223372036854775807 INCREMENT 2147483647;
    CREATE GENERATOR TMP_GEN_42054 START WITH -9223372036854775808 INCREMENT -2147483647;
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.isql(switches=['-x'])
    assert act.clean_stdout == act.clean_expected_stdout


