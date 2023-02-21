#coding:utf-8

"""
ID:          monitoring-tables-03
TITLE:       table MON$COMPILED_STATEMENTS and columns MON$STATEMENTS.MON$COMPILED_STATEMENT_ID and MON$CALL_STACK.MON$COMPILED_STATEMENT_ID
DESCRIPTION: see https://github.com/FirebirdSQL/firebird/commit/3a452630b67f26d100c60234941a40d4468c170e (11-aug-2022)
NOTES:
    [21.02.2023] pzotov
    Checked on 5.0.0.958
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set sqlda_display on;
    set planonly;
    select * from mon$compiled_statements;
    select mon$statements.mon$compiled_statement_id from mon$statements;
    select mon$call_stack.mon$compiled_statement_id from mon$call_stack;
"""

substitutions = [('^((?!sqltype|name:|table:).)*$', ''), ('.*owner:.*', ''), ('.*alias:.*', ''), ('[ ]+', ' '), ('[\t]*', ' ')]

act = isql_act('db', test_script, substitutions = substitutions)

expected_stdout = """
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
      :  name: MON$COMPILED_STATEMENT_ID  alias: MON$COMPILED_STATEMENT_ID
      : table: MON$COMPILED_STATEMENTS  owner: SYSDBA
    02: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
      :  name: MON$SQL_TEXT  alias: MON$SQL_TEXT
      : table: MON$COMPILED_STATEMENTS  owner: SYSDBA
    03: sqltype: 520 BLOB Nullable scale: 0 subtype: 1 len: 8 charset: 4 UTF8
      :  name: MON$EXPLAINED_PLAN  alias: MON$EXPLAINED_PLAN
      : table: MON$COMPILED_STATEMENTS  owner: SYSDBA
    04: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 252 charset: 4 UTF8
      :  name: MON$OBJECT_NAME  alias: MON$OBJECT_NAME
      : table: MON$COMPILED_STATEMENTS  owner: SYSDBA
    05: sqltype: 500 SHORT Nullable scale: 0 subtype: 0 len: 2
      :  name: MON$OBJECT_TYPE  alias: MON$OBJECT_TYPE
      : table: MON$COMPILED_STATEMENTS  owner: SYSDBA
    06: sqltype: 452 TEXT Nullable scale: 0 subtype: 0 len: 252 charset: 4 UTF8
      :  name: MON$PACKAGE_NAME  alias: MON$PACKAGE_NAME
      : table: MON$COMPILED_STATEMENTS  owner: SYSDBA
    07: sqltype: 496 LONG Nullable scale: 0 subtype: 0 len: 4
      :  name: MON$STAT_ID  alias: MON$STAT_ID
      : table: MON$COMPILED_STATEMENTS  owner: SYSDBA


    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
      :  name: MON$COMPILED_STATEMENT_ID  alias: MON$COMPILED_STATEMENT_ID
      : table: MON$STATEMENTS  owner: SYSDBA

    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
      :  name: MON$COMPILED_STATEMENT_ID  alias: MON$COMPILED_STATEMENT_ID
      : table: MON$CALL_STACK  owner: SYSDBA
"""

@pytest.mark.version('>=5.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
