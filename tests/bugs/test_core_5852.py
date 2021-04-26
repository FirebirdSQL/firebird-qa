#coding:utf-8
#
# id:           bugs.core_5852
# title:        There is no check of existance generator and exception when privileges are granted
# decription:   
#                   Confirmed absenceof check on: 3.0.4.32995, 4.0.0.1028
#                   Checked on: 3.0.4.32997: OK, 1.110s.
#                
# tracker_id:   CORE-5852
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
    recreate view v_grants as
    select
        p.rdb$user_type       as usr_type
       ,p.rdb$user            as usr_name
       ,p.rdb$grantor         as who_gave
       ,p.rdb$privilege       as what_can
       ,p.rdb$grant_option    as has_grant
       ,p.rdb$object_type     as obj_type
       ,p.rdb$relation_name   as rel_name
       ,p.rdb$field_name      as fld_name
    from rdb$database r left join rdb$user_privileges p on 1=1 
    where p.rdb$user in( upper('tmp$c5852') )
    order by 1,2,3,4,5,6,7,8
    ;

    create or alter user tmp$c5852 password '123';
    commit;

    grant usage on exception no_such_exc to user tmp$c5852;
    grant usage on generator no_such_gen to user tmp$c5852;
    grant usage on sequence no_such_seq to user tmp$c5852;

    --grant execute on procedure no_such_proc to user tmp$c5852;
    --grant execute on function no_such_func to user tmp$c5852;
    --grant execute on package no_such_pkg to user tmp$c5852;

    commit;

    set list on;
    set count on;

    select 
         usr_type
        ,usr_name
        ,what_can
        ,has_grant
        ,obj_type
        ,rel_name
    from v_grants;
    commit;

    drop user tmp$c5852;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -Exception NO_SUCH_EXC does not exist

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -Generator/Sequence NO_SUCH_GEN does not exist

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -GRANT failed
    -Generator/Sequence NO_SUCH_SEQ does not exist
  """

@pytest.mark.version('>=3.0.4')
def test_core_5852_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

