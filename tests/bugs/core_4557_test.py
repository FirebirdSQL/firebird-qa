#coding:utf-8

"""
ID:          issue-1578
ISSUE:       1578
TITLE:       FB 3.0 crashes on EXIT (or QUIT) command if use UTF8-collation + create domain based on it + issue SHOW DOMAIN
DESCRIPTION:
JIRA:        CORE-4557
"""

import pytest
from firebird.qa import *

init_script = """
  create collation name_coll for utf8 from unicode CASE INSENSITIVE;
  create collation nums_coll for utf8 from unicode CASE INSENSITIVE 'NUMERIC-SORT=1';
  commit;
  create domain dm_name as varchar(80) character set utf8 collate name_coll;
  create domain dm_nums as varchar(20) character set utf8 collate nums_coll;
  commit;
"""

db = db_factory(init=init_script)

test_script = """
  show domain; -- FB crashes if this will be uncommented
  exit;
"""

act = isql_act('db', test_script)

# version: 3.0

expected_stdout_1 = """
  DM_NAME                                DM_NUMS
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_1
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

# version: 4.0

expected_stdout_2 = """
    DM_NAME
    DM_NUMS
"""

@pytest.mark.version('>=4.0')
def test_2(act: Action):
    act.expected_stdout = expected_stdout_2
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

