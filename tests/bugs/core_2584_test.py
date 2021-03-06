#coding:utf-8
#
# id:           bugs.core_2584
# title:        Wrong results for CASE used together with GROUP BY
# decription:   
# tracker_id:   CORE-2584
# min_versions: ['2.5']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- 08.03.2015: removed code based on data in RDB$ tables - they differs in 2.5 vs 3.0.
    recreate table rf(rp int);
    commit;
    
    set term ^;
    execute block as
      declare n int = 250;
    begin
      delete from rf;
      while (n>0) do insert into rf(rp) values( mod(:n, 1+mod(:n,7) ) )returning :n-1 into n;
    end
    ^ set term ;^
    commit;
    
    set list on;
    select
      rp as a,
      case rp
        when 0 then '0'
        when 1 then '1'
        when 2 then '2'
        when 3 then '3'
        when 4 then '4'
      end as b,
      count(*) as cnt
    from rf
    where rp < 5
    group by 1, 2;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                               0
    B                               0
    CNT                             87
    A                               1
    B                               1
    CNT                             52
    A                               2
    B                               2
    CNT                             34
    A                               3
    B                               3
    CNT                             22
    A                               4
    B                               4
    CNT                             14
  """

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

