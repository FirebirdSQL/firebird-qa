#coding:utf-8
#
# id:           bugs.core_6300
# title:        Next attachment id, next statement id - get this info via MON$ query and rdb$get_context()
# decription:
#                   Check SQLDA output by query mon$database columns and context variabled that are described in doc/sql.extensions/README.context_variables2
#                   See also: https://github.com/FirebirdSQL/firebird/commit/22ad236f625716f5f2885f8d9e783cca9516f7b3
#                   Checked on 4.0.0.2170.
#
# tracker_id:
# min_versions: ['4.0']
# versions:     4.0
# qmid:         bugs.core_6300

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('^((?!sqltype|name:).)*$', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    set planonly;
    select mon$guid,mon$file_id,mon$next_attachment,mon$next_statement, rdb$get_context('SYSTEM', 'DB_GUID'), rdb$get_context('SYSTEM', 'DB_FILE_ID')
    from mon$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    01: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 38 charset: 0 NONE
    :  name: MON$GUID  alias: MON$GUID
    02: sqltype: 448 VARYING scale: 0 subtype: 0 len: 255 charset: 2 ASCII
    :  name: MON$FILE_ID  alias: MON$FILE_ID
    03: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    :  name: MON$NEXT_ATTACHMENT  alias: MON$NEXT_ATTACHMENT
    04: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    :  name: MON$NEXT_STATEMENT  alias: MON$NEXT_STATEMENT
    05: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 255 charset: 0 NONE
    :  name: RDB$GET_CONTEXT  alias: RDB$GET_CONTEXT
    06: sqltype: 448 VARYING Nullable scale: 0 subtype: 0 len: 255 charset: 0 NONE
    :  name: RDB$GET_CONTEXT  alias: RDB$GET_CONTEXT
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.charset = 'NONE'
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

