#coding:utf-8
#
# id:           bugs.core_2101
# title:        Bugcheck 249 when attempting to fetch outside the end-of-stream mark for the open PSQL cursor
# decription:   
#                   Confirmed on WI-V2.1.7.18553 Firebird 2.1:
#                   Statement failed, SQLSTATE = XX000
#                   internal Firebird consistency check (pointer page vanished from DPM_next (249), file: dpm.cpp line: 1698)
#                
# tracker_id:   CORE-2101
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('SQLSTATE.*', 'SQLSTATE'), ('line: \\d+,', 'line: x'), ('col: \\d+', 'col: y')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create table t1 ( f1 smallint );
    set term ^ ;
    create procedure p1
    as
      declare v1 smallint;
      declare c1 cursor for ( select f1 from t1 );
    begin
      open c1;
      while (1=1) do
      begin
           fetch c1 into :v1;
           if(row_count = 1) then leave;
      end
      close c1;
    end ^
    set term ; ^
    commit;

    execute procedure p1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY109
    attempt to fetch past the last record in a record stream
    -At procedure 'P1' line: 19, col: 18
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

