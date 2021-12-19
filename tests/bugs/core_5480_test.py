#coding:utf-8
#
# id:           bugs.core_5480
# title:        SUBSTRING startposition smaller than 1 should be allowed
# decription:
#                  Test is based on ticket samples, plus similar checks for non-ascii strings.
#                  Checked on WI-T4.0.0.546 with UTF8 charset. Works fine.
#
# tracker_id:   CORE-5480
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    -- ASCII string tests:
    select '|'  || substring('abcdef' from 0) || '|'         a01 from rdb$database; -- Expected result: 'abcdef'
    select '|'  || substring('abcdef' from 0 for 2) || '|'   a02 from rdb$database; --Expected result: 'a' (and NOT 'ab')
    select '|'  || substring('abcdef' from -5 for 2) || '|'  a03 from rdb$database; --Expected result: ''
    select '|'  || substring('abcdef' from -1 for 3) || '|'  a04 from rdb$database; --Expected result: 'a'
    select '|'  || substring('abcdef' from -2 for 5) || '|'  a05 from rdb$database; --Expected result: 'ab'
    select '|'  || substring('abcdef' from -2147483645 for 2147483647) || '|'  a06 from rdb$database;  -- added case with big values for arguments

    -- multi-byte string tests:
    -- Euro sign (requires three bytes for encoding) concatenated
    -- with letters from Danish, German & Iceland alphabets:
    select '|'  || substring('€åßðéæø' from 0) || '|'        n01 from rdb$database;
    select '|'  || substring('€åßðéæø' from 0 for 2) || '|'  n02 from rdb$database;
    select '|'  || substring('€åßðéæø' from -5 for 2) || '|' n03 from rdb$database;
    select '|'  || substring('€åßðéæø' from -1 for 3) || '|' n04 from rdb$database;
    select '|'  || substring('€åßðéæø' from -2 for 5) || '|' n05 from rdb$database;
    select '|'  || substring('€åßðéæø' from -2147483645 for 2147483647) || '|' n06 from rdb$database;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A01                             |abcdef|
    A02                             |a|
    A03                             ||
    A04                             |a|
    A05                             |ab|
    A06                             |a|

    N01                             |€åßðéæø|
    N02                             |€|
    N03                             ||
    N04                             |€|
    N05                             |€å|
    N06                             |€|
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute(charset='utf8')
    assert act_1.clean_expected_stdout == act_1.clean_stdout

