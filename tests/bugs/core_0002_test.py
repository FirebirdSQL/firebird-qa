#coding:utf-8
#
# id:           bugs.core_0002
# title:        Incorrect value returned with execute statement calculation
# decription:
# tracker_id:   CORE-0002
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    create table t1 (
        campo1 numeric(15,2),
        campo2 numeric(15,2)
    );
    commit;
    set term ^;
    create procedure teste
    returns (
        retorno numeric(15,2))
    as
    begin
      execute statement 'select first 1 (campo1*campo2) from t1' into :retorno;
      suspend;
    end
    ^
    set term ;^
    commit;

    insert into t1 (campo1, campo2) values (10.5, 5.5);
    commit;

    select * from teste;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RETORNO                         57.75
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

