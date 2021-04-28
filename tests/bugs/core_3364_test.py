#coding:utf-8
#
# id:           bugs.core_3364
# title:        Blob filter to translate internal debug info into text representation
# decription:   
# tracker_id:   CORE-3364
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('RDB\\$DEBUG_INFO', ''), ('-', ''), ('[0-9]+[ ]+[0-9]+[ ]+[0-9]+', '')]

init_script_1 = """
    set term ^;
    create or alter procedure sp_test(a_n smallint) returns(n_fact bigint) as
    begin
        n_fact = iif(a_n > 0, a_n, 0);
    
        while (a_n > 1) do 
        begin
          n_fact = n_fact * (a_n - 1);
          a_n = a_n -1;
        end
        suspend;
    end
    ^
    set term ;^
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set blob all;
    select rdb$debug_info from rdb$procedures where upper(rdb$procedure_name) = upper('sp_test');
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$DEBUG_INFO                  1a:f0
    Parameters:
    Number Name                             Type
    --------------------------------------------------
    0 A_N                              INPUT
    0 N_FACT                           OUTPUT
    Variables:
    Number Name
    -------------------------------------------
    0 N_FACT
    BLR to Source mapping:
    BLR offset       Line     Column
    --------------------------------
    36          2          5
    38          3          9
    73          5          9
    92          6          9
    94          7         11
    116         8         11
    142        10          9
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

