#coding:utf-8
#
# id:           bugs.core_3997
# title:        Join using RDB$DB_KEY produce NATURAL plan
# decription:   
#                   Confirmed on WI-V2.5.1.26351, it issues:
#                   PLAN JOIN (T_KEY NATURAL, T NATURAL)
#                
# tracker_id:   CORE-3997
# min_versions: ['2.5.7']
# versions:     2.5.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table t (f integer);
    recreate table t_key (k char(8) character set octets);
    commit;

    set term ^;
    execute block as
      declare i int = 10000;
    begin
     While (i>0) do
      begin
       insert into t values (:i);
       i = i-1;
      end
    end^
    set term ;^
    commit;

    insert into t_key select rdb$db_key from t where f=1;
    commit;

    set planonly;
    select f 
    from t join t_key on 
    t.rdb$db_key=t_key.k;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN JOIN (T_KEY NATURAL, T INDEX ())
"""

@pytest.mark.version('>=2.5.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

