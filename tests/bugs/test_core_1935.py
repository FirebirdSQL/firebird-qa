#coding:utf-8
#
# id:           bugs.core_1935
# title:        SIMILAR TO character classes are incorrectly recognized
# decription:   
#                   Checked on:
#                       2.5.9.27107: OK, 0.406s.
#                       3.0.4.32924: OK, 2.250s.
#                       4.0.0.916: OK, 1.562s.
#                
# tracker_id:   CORE-1935
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    -- two subsequent classes in double braces, concatenated together:
    select 11 as r from rdb$database where '1a' similar to '[[:DIGIT:]][[:ALPHA:]]'; -- output: 11

    -- comparison with SINGLE class of ONE character length: either digit or whitespace or alpha:
    select 12 as r from rdb$database where '1a' similar to '[[:DIGIT:][:WHITESPACE:][:ALPHA:]]'; -- no output, no error

    -- comparison with character '2' followed by either digit or whitespace or alpha (should produce non-empty result):
    select 21 as r from rdb$database where '2a' similar to '2[[:DIGIT:][:WHITESPACE:][:ALPHA:]]'; -- output: 21

    -- comparison with SINGLE class of ONE character length: digit either alnum either alpha
    select 22 as r from rdb$database where '2a' similar to '[[:DIGIT:][:ALNUM:][:ALPHA:]]'; -- no output, no error

    -- comparison with TWO classes: 1st is result of concatenation alnum and whitespace, 2ns is alnum:
    select 31 as r from rdb$database where '3a' similar to '[[:ALNUM:][:WHITESPACE:]][[:ALNUM:]]'; -- 31

    -- comparison with TWO classes: 1st alnum, 2nd is result of concatenation whitespace and digit:
    select 32 as r from rdb$database where '32' similar to '[[:ALNUM:]][[:WHITESPACE:][:DIGIT:]]'; -- 32

    select 41 as r from rdb$database where '4a' SIMILAR TO '[%[:DIGIT:][:ALNUM:]]%';

    select 42 as r from rdb$database where '4b' SIMILAR TO '[[:DIGIT:][:ALNUM:]]'; -- no output, no error

    select 51 as r from rdb$database where '5a' SIMILAR TO '%[[:DIGIT:][:ALNUM:]%]'; -- 51

    select 52 as r from rdb$database where '5a' similar to '[%[:DIGIT:][:ALPHA:]][[:ALNUM:]%]'; -- 52
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    R                               11
    R                               21
    R                               31
    R                               32
    R                               41
    R                               51
    R                               52
  """

@pytest.mark.version('>=2.5')
def test_core_1935_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

