#coding:utf-8
#
# id:           bugs.core_4590
# title:        Change type of returning value of CHAR_LENGTH, BIT_LENGTH and OCTET_LENGTH of BLOBs to bigint
# decription:   
# tracker_id:   CORE-4590
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!sqltype).)*$', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display;
    set planonly;
    select
        char_length(rdb$description) clen
        ,bit_length(rdb$description) blen
        ,octet_length(rdb$description) olen
    from rdb$database;
    -- No more output of charset name for NON-text field, see:
    -- http://sourceforge.net/p/firebird/code/61779 // 10.06.2015
    -- Enhance metadata display - show charset only for fields where it makes sense
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    02: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
  """

@pytest.mark.version('>=3.0')
def test_core_4590_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

