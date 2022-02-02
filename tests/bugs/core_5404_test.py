#coding:utf-8

"""
ID:          issue-5677
ISSUE:       5677
TITLE:       Inconsistent column/line references when PSQL definitions return errors
DESCRIPTION:
  ### WARNING ###
  Following code is intentionaly aborted in the middle point because some cases are not
  covered by fix of this ticket (see also issue in the ticket, 22/Nov/16 06:10 PM).
JIRA:        CORE-5404
FBTEST:      bugs.core_5404
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set term ^;
    create or alter procedure dsql_field_err1 as
      declare i int;
    begin
      select "" from rdb$database into i; -- Column unknown.
    end
    ^

    create or alter procedure dsql_field_err2 as
      declare i int;
    begin
      select foo from rdb$database into i;
    end
    ^
    set term ;^

    quit; ---------------------------------------  Q U I T   -------------------  (TEMPLY)

    set term ^;
    create or alter procedure dsql_count_mismatch as
      declare i int;
      declare k int;
    begin
      select 1 from rdb$database into i, k; -- Count of column list and variable list do not match.
    end
    ^

    create or alter procedure dsql_invalid_expr  as
      declare i int;
      declare j varchar(64);
      declare k int;
    begin
      select RDB$RELATION_ID,RDB$CHARACTER_SET_NAME, count(*)
      from rdb$database
      group by 1
      into i, j, k;
    end
    ^

    create or alter procedure dsql_agg_where_err as
      declare i int;
    begin
      select count(*)
      from rdb$database
      group by count(*) -- Cannot use an aggregate function in a GROUP BY clause.
      into i;
    end
    ^

    create or alter procedure dsql_agg_nested_err as
      declare i int;
    begin
      select count( max(1) )  -- Nested aggregate functions are not allowed.
      from rdb$database
      into i;
    end
    ^

    create or alter procedure dsql_column_pos_err as
      declare i int;
    begin
      select 1
      from rdb$database
      order by 1, 2     -- Invalid column position used in the @1 clause
      into i;
    end
    ^
    set term ;^

"""

act = isql_act('db', test_script,
               substitutions=[('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+',
                               '-At line: column:')])

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Zero length identifiers are not allowed
    -At line 4, column 10

    Statement failed, SQLSTATE = 42S22
    unsuccessful metadata update
    -CREATE OR ALTER PROCEDURE DSQL_FIELD_ERR2 failed
    -Dynamic SQL Error
    -SQL error code = -206
    -Column unknown
    -FOO
    -At line 4, column 10
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

