#coding:utf-8
#
# id:           bugs.core_5404
# title:        Inconsistent column/line references when PSQL definitions return errors
# decription:   
#                   ### WARNING ###
#                   Following code is intentionaly aborted in the middle point because some cases are not 
#                   covered by fix of this ticket (see also issue in the ticket, 22/Nov/16 06:10 PM).
#                
# tracker_id:   CORE-5404
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('-At line[:]{0,1}[\\s]+[\\d]+,[\\s]+column[:]{0,1}[\\s]+[\\d]+', '-At line: column:')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
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
def test_core_5404_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

