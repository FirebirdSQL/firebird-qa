#coding:utf-8
#
# id:           bugs.core_5536
# title:        Connections compressed and encrypted in MON$ATTACHMENTS table
# decription:   
#                   26.01.2019. Replaced old field names (MON$CONNECTION_COMPRESSED, MON$CONNECTION_ENCRYPTED) with new ones. 
#                   Removed trivial 'select 1', use SQLDA_DISPLAY to have explicit output columns type (boolean).
#                   Checked on:
#                       4.0.0.1340: OK, 1.828s.
#                       4.0.0.1410: OK, 1.969s.
#                   Previous check: 4.0.0.728: OK, 0.797s.
#                
# tracker_id:   CORE-5536
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
    set planonly;
    set sqlda_display on;
    select mon$wire_compressed, mon$wire_encrypted
    from mon$attachments
    where mon$attachment_id = current_connection
    ;
    -- Fields that were used before:
    -- MON$CONNECTION_COMPRESSED in (false, true)
    -- and MON$CONNECTION_ENCRYPTED in (false, true)
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 0

    PLAN (MON$ATTACHMENTS NATURAL)

    OUTPUT message field count: 2
    01: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
      :  name: MON$WIRE_COMPRESSED  alias: MON$WIRE_COMPRESSED
      : table: MON$ATTACHMENTS  owner: SYSDBA
    02: sqltype: 32764 BOOLEAN Nullable scale: 0 subtype: 0 len: 1
      :  name: MON$WIRE_ENCRYPTED  alias: MON$WIRE_ENCRYPTED
      : table: MON$ATTACHMENTS  owner: SYSDBA
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

