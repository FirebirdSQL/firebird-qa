#coding:utf-8
#
# id:           functional.procedure.create.16
# title:        Type Flaq for Stored Procedures
# decription:   
#                   Checked on:
#                       2.5.9.27126: OK, 0.579s.
#                       3.0.5.33086: OK, 1.219s.
#                       4.0.0.1378: OK, 8.219s.
#                
# tracker_id:   CORE-779
# min_versions: []
# versions:     2.5
# qmid:         functional.procedure.create.create_procedure_16

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """
    set term ^;
    create or alter procedure with_suspend (nom1 varchar(20) character set iso8859_1 collate fr_fr)
    returns (nom3 varchar(20) character set iso8859_1 collate iso8859_1) as
        declare variable nom2 varchar(20) character set iso8859_1 collate fr_ca;
    begin
        nom2=nom1;
        nom3=nom2;
        suspend;
    end ^
    
    create or alter procedure no_suspend returns(p1 smallint) as
    begin
        p1=1;
    end ^
    set term ;^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select p.rdb$procedure_name, p.rdb$procedure_type
    from rdb$procedures p
    where upper(p.rdb$procedure_name) in ( upper('with_suspend'), upper('no_suspend') )
    order by 1;  
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$PROCEDURE_NAME              NO_SUSPEND
    RDB$PROCEDURE_TYPE              2

    RDB$PROCEDURE_NAME              WITH_SUSPEND
    RDB$PROCEDURE_TYPE              1
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

