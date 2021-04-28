#coding:utf-8
#
# id:           bugs.core_5565
# title:        No integer division possible in dialect 1
# decription:   
#                  Reproduced fail on build 4.0.0.651.
#                  Build 4.0.0.680: OK, 1.046s
#                
# tracker_id:   CORE-5565
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set sql dialect 1;
    commit;
    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    set term ^;
    execute block as
        declare c int;
    begin
        select 1/1 as x from rdb$database into c;
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.execute()

