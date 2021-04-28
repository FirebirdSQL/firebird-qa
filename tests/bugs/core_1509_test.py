#coding:utf-8
#
# id:           bugs.core_1509
# title:        Conversion from double to varchar insert trailing spaces
# decription:   
#                  Confirmed bug on WI-V2.0.0.12724: output of cast(cast(0e0 as double precision) as varchar(32))||'z'
#                  is: |0.0000000000000000    z| (four spaces inside)
#                
# tracker_id:   CORE-1509
# min_versions: []
# versions:     2.5.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
     set list on;
     select
          iif( position(' z' in t1)>0, 'BAD: >' || t1 || '<', 'OK.') as chk1
         ,iif( position(' z' in t2)>0, 'BAD: >' || t2 || '<', 'OK.') as chk2
         ,iif( position(' z' in t3)>0, 'BAD: >' || t3 || '<', 'OK.') as chk3
     from (
         select
              cast(exp(-744.0346068132731393)-exp(-745.1332191019410399) as varchar(32))||'z' t1
             ,cast(sin(0) as varchar(32))||'z' t2
             ,cast(cast(0e0 as double precision) as varchar(32))||'z' t3
         from rdb$database
     );
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CHK1                            OK.
    CHK2                            OK.
    CHK3                            OK.
  """

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

