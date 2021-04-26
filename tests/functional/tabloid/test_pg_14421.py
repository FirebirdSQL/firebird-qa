#coding:utf-8
#
# id:           functional.tabloid.pg_14421
# title:        UPDATE/DETERE RETURNING should issue only one row when applying to table with self-referencing FK
# decription:   
#                  Original issue:
#                  https://www.postgresql.org/message-id/cakfquwyrb5iyfqs6o9mmtbxp96l40bxpnfgosj8xm88ag%2b5_aa%40mail.gmail.com
#                
# tracker_id:   
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    recreate table test(
        id int primary key,
        pid int references test(id) on delete cascade on update cascade
    );
    insert into test values (1, null);
    insert into test values (2, 1);
    insert into test values (3, 2);
    insert into test values (4, 2);
    insert into test values (5, 2);
    insert into test values (6, 2);
    insert into test values (7, 2);
    commit;

    delete from test
       where id = 2
       returning id as old_id
    ;
    rollback;


    update test set id=9 where id=2 
    returning old.id as old_id, new.id as new_id
    ;

    rollback;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    OLD_ID                          2



    OLD_ID                          2
    NEW_ID                          9
  """

@pytest.mark.version('>=3.0')
def test_pg_14421_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

