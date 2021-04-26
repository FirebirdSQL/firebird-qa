#coding:utf-8
#
# id:           bugs.core_5279
# title:        Granting access rights to view is broken
# decription:   
#                  Confirmed bug on 3.0.0.32483 (official 3.0 release).
#                  Checked on 3.0.1.32539, 4.0.0.262 - works fine.
#                
# tracker_id:   CORE-5279
# min_versions: ['3.0.1']
# versions:     3.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter user tmp$c5279 password '123';
    commit;
    recreate table test (id integer);
    recreate table test1 (id integer);
    commit;
    create or alter view v_test as 
    select * 
    from test 
    where id in (select id from test1);
    commit;
    grant select on v_test to public;
    grant select on test1 to view v_test; 
    commit;
    insert into test(id) values(1);
    insert into test(id) values(2);
    insert into test(id) values(3);

    insert into test1(id) values(3);
    insert into test1(id) values(4);
    insert into test1(id) values(5);
    commit;

    connect '$(DSN)' user tmp$c5279 password '123';
    set count on;
    set list on;
    select current_user as who_am_i, v.* from v_test v;
    commit;
    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$c5279;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    WHO_AM_I                        TMP$C5279
    ID                              3
    Records affected: 1
  """

@pytest.mark.version('>=3.0.1')
def test_core_5279_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

