#coding:utf-8

"""
ID:          issue-5361
ISSUE:       5361
TITLE:       Lost the charset ID in selection of array element
DESCRIPTION:
JIRA:        CORE-5074
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    recreate table test(
        a char(10)[0:3] character set octets
    );
    set sqlda_display on;
    select a[0] from test;
"""

act = isql_act('db', test_script)

expected_stdout = """
    INPUT message field count: 0

    OUTPUT message field count: 1
    01: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 10 charset: 1 OCTETS
      :  name: A  alias: A
      : table: TEST  owner: SYSDBA
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

