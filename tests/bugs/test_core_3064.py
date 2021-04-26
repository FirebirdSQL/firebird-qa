#coding:utf-8
#
# id:           bugs.core_3064
# title:        Using both the procedure name and alias inside an explicit plan crashes the server
# decription:   
# tracker_id:   CORE-3064
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = [('offset .*', '')]

init_script_1 = """
    set term ^ ;
    create or alter procedure get_dates (
        adate_from date,
        adate_to date )
    returns (
        out_date date )
    as
      declare variable d date;
    begin
      d = adate_from;
      while (d<=adate_to) do
        begin
          out_date = d;
          suspend;
          d = d + 1;
        end
    end^
    set term ; ^
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set planonly;
    select * from get_dates( 'yesterday', 'today' ) PLAN (GET_DATES NATURAL);
    select * from get_dates( 'yesterday', 'today' ) p PLAN (P NATURAL);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
Statement failed, SQLSTATE = 42S02
Dynamic SQL Error
-SQL error code = -104
-Invalid command
-there is no alias or table named GET_DATES at this scope level
Statement failed, SQLSTATE = HY000
invalid request BLR at offset 50
-BLR syntax error: expected TABLE at offset 51, encountered 132
  """

@pytest.mark.version('>=2.5.1')
def test_core_3064_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

