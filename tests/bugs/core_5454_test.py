#coding:utf-8
#
# id:           bugs.core_5454
# title:        INSERT into updatable view without explicit field list failed
# decription:   
#                   Confirmed bug on WI-T4.0.0.463, got:
#                      Statement failed, SQLSTATE = 21S01
#                      Dynamic SQL Error
#                      -SQL error code = -804
#                      -Count of read-write columns does not equal count of values
#                   Checked on WI-T4.0.0.503 - works fine.
#                   NB: this bug was NOT (yet ?) fixed for 3.0 ==> min_version = 4.0
#                   (checked on WI-V3.0.2.32670, 17-jan-2017).
#                
# tracker_id:   CORE-5454
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
    recreate view v_test as select 1 x from rdb$database;
    commit;

    recreate table test1(id int, x int);
    recreate table test2(id int, x int);

    recreate view v_test as
    select * from test1
    union all
    select * from test2;

    set term ^;
    create trigger v_test_dml for v_test before insert as
      declare i integer;
    begin
      i = mod(new.id, 2);
      if (i = 0) then
        insert into test1 values (new.id, new.x);
      else if (i = 1) then
        insert into test2 values (new.id, new.x);
    end
    ^
    set term ;^
    commit; 

    set count on;
    insert into v_test values(123, 321);

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 1
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

