#coding:utf-8
#
# id:           bugs.core_4233
# title:        In PSQL modules with declared cursors engine could assign value to the wrong variable
# decription:   
# tracker_id:   CORE-4233
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """
    set term ^;
    create or alter procedure hidden_vars
      returns (out_a int, out_b1 int, out_b2 int)
    as
    declare a int;
    declare c cursor for
      (select 
          coalesce( (select count(*) from rdb$relations), -1) 
          -- Aliasing of expression results in derived tables is mandatory in 3.0
          -- otherwise get error about metadata updating:
          -- -no column name specified for column number 1 in derived table 
          -- <missing arg #2 - possibly status vector overflow>
          as tabs_cnt -- <<<<<<<<<<<<<<< nb <<<<<<<<<<<
          from rdb$database
      );
    declare b int = 0;
    begin
      out_b1 = b;
    
      open c;
      fetch c into :a;
      close c;
    
      out_a = a;
      out_b2 = b;
      b = b + 1;
      suspend;
    end ^
    set term ; ^
    commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    select out_b1, out_b2 from hidden_vars;
    select out_b1, out_b2 from hidden_vars;
    select out_b1, out_b2 from hidden_vars;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """      OUT_B1       OUT_B2
============ ============
           0            0
      OUT_B1       OUT_B2
============ ============
           0            0
      OUT_B1       OUT_B2
============ ============
           0            0
"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

