#coding:utf-8
#
# id:           bugs.core_5773
# title:        PSQL cursor doesn't see inserted record
# decription:   
#                     Confirmed wrong result on 3.0.4.32924
#                     Works fine on 3.0.4.32939: OK, 1.453s.
#                 
# tracker_id:   CORE-5773
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    create or alter procedure sp_test as begin end;
    recreate table test (id bigint);
    commit;

    set term ^;
    create or alter procedure sp_test returns (
        rowcount integer
    ) as
        declare id bigint;
        declare c_ins cursor for (
            select id from test
        );
    begin
        insert into test(id) values(1);
        open c_ins;
            fetch c_ins into :id;
            rowcount = row_count;
            suspend;
        close c_ins;
    end^
    set term ;^
    select * from sp_test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ROWCOUNT                        1
    Records affected: 1
  """

@pytest.mark.version('>=3.0.4')
def test_core_5773_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

