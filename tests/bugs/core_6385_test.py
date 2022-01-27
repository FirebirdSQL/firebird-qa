#coding:utf-8

"""
ID:          issue-6624
ISSUE:       6624
TITLE:       Wrong line and column information after IF statement
DESCRIPTION:
  DO NOT make indentation or excessive empty lines in the code that is executed by ISQL.
JIRA:        CORE-6385
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
set term ^;
execute block
as
    declare n integer;
begin
    if (1 = 1) then
        n = 1;
    n = n / 0;
end^
set term ;^
"""

act = isql_act('db', test_script, substitutions=[('^((?!At\\s+block\\s+line).)*$', ''),
                                                 ('[ \t]+', ' ')])

expected_stderr = """
-At block line: 7, col: 5
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
