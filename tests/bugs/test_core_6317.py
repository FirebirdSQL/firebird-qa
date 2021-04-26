#coding:utf-8
#
# id:           bugs.core_6317
# title:        Server is crashing on long GRANT statement
# decription:   
#                   Confirmed crash on: 4.0.0.1963 SC; 3.0.6.33289 SC
#                   Checked on: 4.0.0.2006 SS/SC, 3.0.6.33296 SS/SC -- all fine.
#                
# tracker_id:   CORE-6317
# min_versions: ['3.0.6']
# versions:     3.0.6
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.6
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    set wng off;
    create or alter user tmp$c6317 password '123';
    revoke all on all from tmp$c6317;
    commit;

    recreate table test (id integer);
    insert into test(id) values(1);
    commit;

    grant select, select, select, select, select, select, select, select, select, select, select, select, select, select, select, select on test to tmp$c6317;
    commit;

    set list on;
    select
         rdb$user                        -- tmp$c6317
        ,rdb$relation_name               -- test
        ,rdb$privilege                   -- S
        ,rdb$grant_option                -- 0
        ,rdb$field_name                  -- <null>
        ,rdb$object_type                 -- 0
    from rdb$user_privileges p
    where upper(p.rdb$relation_name) = upper('test') and rdb$user = upper('tmp$c6317')
    order by rdb$privilege
    ;
    commit;

    connect '$(DSN)' user tmp$c6317 password '123';
    select * from test;
    commit;

    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$c6317;
    commit;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$USER                        TMP$C6317
    RDB$RELATION_NAME               TEST
    RDB$PRIVILEGE                   S
    RDB$GRANT_OPTION                0
    RDB$FIELD_NAME                  <null>
    RDB$OBJECT_TYPE                 0

    ID                              1
  """

@pytest.mark.version('>=3.0.6')
def test_core_6317_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

