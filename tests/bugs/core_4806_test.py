#coding:utf-8

"""
ID:          issue-5104
ISSUE:       5104
TITLE:       Regression: generators can be seen/modified by unprivileged users
DESCRIPTION:
  We create sequence ('g') and three users and one role.
  First user ('big_brother') is granted to use generator directly.
  Second user ('bill_junior') is gratned to use generator via ROLE ('stockmgr').
  Third user ('maverick') has no grants to use neither on role nor on generator.
  Then we try to change value of generator by call gen_id(g,1) by create apropriate
  connections (for each of these users).
  First and second users must have ability both to change generator and to see its
  values using command 'SHOW SEQUENCE'.
  Also, we do additional check for second user: try to connect WITHOUT specifying role
  and see/change sequence. Error must be in this case (SQLSTATE = 28000).
  Third user must NOT see neither value of generator nor to change it (SQLSTATE = 28000).
NOTES:
[18.08.2020]
  FB 4.x has incompatible behaviour with all previous versions since build 4.0.0.2131 (06-aug-2020):
  statement 'CREATE SEQUENCE <G>' will create generator with current value LESS FOR 1 then it was before.
  Thus, 'create sequence g;' followed by 'show sequence;' will output "current value: -1" (!!) rather than 0.
  See also CORE-6084 and its fix: https://github.com/FirebirdSQL/firebird/commit/23dc0c6297825b2e9006f4d5a2c488702091033d

  This is considered as *expected* and is noted in doc/README.incompatibilities.3to4.txt
  Because of this, it was decided to filter out concrete values that are produced in 'SHOW SEQUENCE' command.
JIRA:        CORE-4806
"""

import pytest
from firebird.qa import *

db = db_factory()

user_a = user_factory('db', name='Maverick', password='123')
user_b = user_factory('db', name='Big_Brother', password='456')
user_c = user_factory('db', name='Bill_Junior', password='789')
role_a = role_factory('db', name='stockmgr')

test_script = """
    set wng off;
    recreate sequence g;
    commit;

    grant usage on sequence g to big_brother;
    grant usage on sequence g to role stockmgr;
    grant stockmgr to Bill_Junior;
    commit;
    show grants;

    set list on;

    connect '$(DSN)' user 'BIG_BROTHER' password '456';
    select current_user, current_role from rdb$database;
    show sequ g;
    select gen_id(g, -111) as new_gen from rdb$database;
    commit;

    connect '$(DSN)' user 'BILL_JUNIOR' password '789' role 'STOCKMGR'; -- !! specify role in UPPER case !!
    select current_user, current_role from rdb$database;
    show sequ g;
    select gen_id(g, -222) as new_gen from rdb$database;
    commit;

    connect '$(DSN)' user 'BILL_JUNIOR' password '789';
    select current_user, current_role from rdb$database;

    -- 'show sequ' should produce error:
    --    Statement failed, SQLSTATE = 28000
    --    no permission for USAGE access to GENERATOR G
    --    There is no generator G in this database
    -- (for user 'Bill_Junior' who connects w/o ROLE and thus has NO rights to see that sequence)
    show sequ g;

    -- 'select gen_id(...)' should produce error:
    --    Statement failed, SQLSTATE = 28000
    --    no permission for USAGE access to GENERATOR G
    -- (for user 'Bill_Junior' who connects w/o ROLE and thus has NO rights to see that sequence)
    select gen_id(g, -333) as new_gen from rdb$database;
    commit;

    connect '$(DSN)' user 'MAVERICK' password '123';
    select current_user, current_role from rdb$database;


    -- 'show sequ' should produce error:
    --    Statement failed, SQLSTATE = 28000
    --    no permission for USAGE access to GENERATOR G
    --    There is no generator G in this database
    -- (for user 'maverick' who has NO rights at all)
    show sequ g;

    -- 'select gen_id(...)' should produce error:
    --    Statement failed, SQLSTATE = 28000
    --    no permission for USAGE access to GENERATOR G
    -- (for user 'maverick' who has NO rights at all)
    select gen_id(g, -444) as new_gen from rdb$database;

    commit;
"""

act = isql_act('db', test_script, substitutions=[('-Effective user is.*', ''),
                                                 ('current value.*', 'current value')])

expected_stdout = """
    /* Grant permissions for this database */
    GRANT STOCKMGR TO BILL_JUNIOR
    GRANT USAGE ON SEQUENCE G TO USER BIG_BROTHER
    GRANT USAGE ON SEQUENCE G TO ROLE STOCKMGR

    USER                            BIG_BROTHER
    ROLE                            NONE
    Generator G, current value: 0, initial value: 0, increment: 1
    NEW_GEN                         -111

    USER                            BILL_JUNIOR
    ROLE                            STOCKMGR
    Generator G, current value: -111, initial value: 0, increment: 1
    NEW_GEN                         -333

    USER                            BILL_JUNIOR
    ROLE                            NONE

    USER                            MAVERICK
    ROLE                            NONE
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    no permission for USAGE access to GENERATOR G
    There is no generator G in this database

    Statement failed, SQLSTATE = 28000
    no permission for USAGE access to GENERATOR G

    Statement failed, SQLSTATE = 28000
    no permission for USAGE access to GENERATOR G
    There is no generator G in this database

    Statement failed, SQLSTATE = 28000
    no permission for USAGE access to GENERATOR G
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, user_a: User, user_b: User, user_c: User, role_a: Role):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

