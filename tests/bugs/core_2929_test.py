#coding:utf-8
#
# id:           bugs.core_2929
# title:        "Invalid ESCAPE sequence" when connecting to the database
# decription:   
# tracker_id:   CORE-2929
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set wng off;
    set list on;

    recreate table t(id int, who_am_i varchar(31) default current_user, whats_my_role varchar(31) default current_role); 
    commit;
    insert into t(id) values(0); 
    commit;

    create user "#" password '#'; 
    create role "##"; 
    commit;

    grant "##" to "#"; 
    commit;

    grant select, insert, update, delete on t to role "##";
    commit;

    connect '$(DSN)' user "#" password '#' role "##";
    insert into t(id) values(1);
    insert into t(id) values(2);
    update t set id = -id where id = 1;
    delete from t where id = 0;

    select * from t order by id;
    commit;

    connect '$(DSN)' user 'SYSDBA' password 'masterkey';
    drop role "##";
    drop user "#";
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID                              -1
    WHO_AM_I                        #
    WHATS_MY_ROLE                   ##

    ID                              2
    WHO_AM_I                        #
    WHATS_MY_ROLE                   ##
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

