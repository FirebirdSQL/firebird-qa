#coding:utf-8
#
# id:           bugs.core_4836
# title:        Grant update(c) on t to U01 with grant option: user U01 will not be able to `revoke update(c) on t from <user | role>` if this `U01` do some DML before revoke
# decription:   
# tracker_id:   CORE-4836
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!C4836|R4836).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter user tmp$c4836 password '123' grant admin role;
    create role tmp$r4836;
    recreate table test(id int, text varchar(30));
    
    grant select on test to public;
    grant update(text) on test to tmp$c4836 with grant option;
    commit;
    
    connect '$(DSN)' user tmp$c4836 password '123';
    
    grant update (text) on test to tmp$r4836;
    commit;
    show grants;
    commit;
    
    select * from test; -- this DML prevented to do subsequent `revoke update(text) on test from role` on build 3.0.0.31873
    
    commit;
    
    revoke update(text) on test from role tmp$r4836;
    commit;
    
    show grants;
    commit;
    
    connect '$(DSN)' user sysdba password 'masterkey';
    drop role tmp$r4836;
    drop user tmp$c4836;
    drop table test;
    commit; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    GRANT UPDATE (TEXT) ON TEST TO USER TMP$C4836 WITH GRANT OPTION
    GRANT UPDATE (TEXT) ON TEST TO ROLE TMP$R4836 GRANTED BY TMP$C4836
    GRANT UPDATE (TEXT) ON TEST TO USER TMP$C4836 WITH GRANT OPTION
  """

@pytest.mark.version('>=3.0')
def test_core_4836_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

