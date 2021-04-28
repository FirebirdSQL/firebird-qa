#coding:utf-8
#
# id:           bugs.core_4125
# title:        Using COLLATE UNICODE_CI_AI in WHERE clause (not indexed) is extremely slow
# decription:   
# tracker_id:   CORE-4125
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """
    create or alter view test as
    with recursive
    r as (select 0 i from rdb$database union all select r.i+1 from r where r.i<98)
    select cast(r1.i*100 + r0.i as varchar(10)) as fx
    from r r1, r r0;
    commit;
  """

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Checked on 2.5.1: ratio = ~105, on 2.5.2: ~132, since 2.5.3: ~1.
    set list on;
    set term ^;
    execute block returns(result varchar(50) ) as
      declare t0 timestamp;
      declare t1 timestamp;
      declare t2 timestamp;
      declare n int;
      declare r numeric(18,3);
    begin
      t0='now';
      select count(*) from test where fx collate unicode_ci like '%8%' into n;
      t1='now';
      select count(*) from test where fx collate unicode_ci_ai like '%8%' into n;
      t2='now';
      n = datediff(millisecond from t1 to t2);
      r = 1.000 * n / nullif(datediff(millisecond from t0 to t1), 0);
      if (r is null and n < 100 or r <= 5) then result = 'TIME RATIO IS OK.';
      else result = 'BAD RATIO: '||coalesce(r,' > 100 vs 0.');
    
      suspend;
    end
    ^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT                          TIME RATIO IS OK.
  """

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

