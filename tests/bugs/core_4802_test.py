#coding:utf-8

"""
ID:          issue-5100
ISSUE:       5100
TITLE:       Regression: GRANT UPDATE(<some_column>) on <T> acts like grant update on ALL columns of <T>
DESCRIPTION:
JIRA:        CORE-4802
FBTEST:      bugs.core_4802
"""

import pytest
from firebird.qa import *

db = db_factory()

user_a = user_factory('db', name='BIG_BROTHER', password='123')
user_b = user_factory('db', name='SENIOR_MNGR', password='456')
user_c = user_factory('db', name='JUNIOR_MNGR', password='789')
role_a = role_factory('db', name='FLD_FOR_SENIORS_UPDATER')
role_b = role_factory('db', name='FLD_FOR_JUNIORS_UPDATER')

test_script = """
    set wng off;

    recreate table test(fld_for_seniors varchar(70), fld_for_juniors varchar(70));
    commit;

    grant select on test to PUBLIC;

    grant update(fld_for_seniors) on test to BIG_BROTHER;
    commit;

    grant update(fld_for_seniors) on test to FLD_FOR_SENIORS_UPDATER;
    grant update(fld_for_juniors) on test to FLD_FOR_JUNIORS_UPDATER;

    grant FLD_FOR_SENIORS_UPDATER to SENIOR_MNGR;
    grant FLD_FOR_JUNIORS_UPDATER to JUNIOR_MNGR;
    commit;

    show grants;

    insert into test values( 'created by '||upper(current_user), 'created by '||lower(current_user) );
    commit;
    set list on;

    --set echo on;

    connect '$(DSN)' user 'BIG_BROTHER' password '123';
    select current_user, current_role from rdb$database;
    update test set fld_for_seniors = 'updated by '||upper(current_user)||', role: '||upper(current_role);
    select * from test;

    update test set fld_for_juniors = 'updated by '||lower(current_user)||', role: '||lower(current_role);
    select * from test;
    commit;
    ---------------------------------------------------------------

    connect '$(DSN)' user 'SENIOR_MNGR' password '456' role 'FLD_FOR_SENIORS_UPDATER';
    select current_user, current_role from rdb$database;
    update test set fld_for_seniors = 'updated by '||upper(current_user)||', role: '||upper(current_role);
    select * from test;

    update test set fld_for_juniors ='updated by '||lower(current_user)||', role: '||lower(current_role);
    select * from test;
    commit;
    ---------------------------------------------------------------

    connect '$(DSN)' user 'JUNIOR_MNGR' password '789' role 'FLD_FOR_JUNIORS_UPDATER';
    select current_user, current_role from rdb$database;
    update test set fld_for_seniors = 'updated by '||upper(current_user)||', role: '||upper(current_role);
    select * from test;

    update test set fld_for_juniors ='updated by '||lower(current_user)||', role: '||lower(current_role);
    select * from test;
    commit;
"""

act = isql_act('db', test_script, substitutions=[('GRANT.*TMP.*', ''), ('-Effective user is.*', '')])

expected_stdout = """
    /* Grant permissions for this database */
    GRANT UPDATE (FLD_FOR_SENIORS) ON TEST TO USER BIG_BROTHER
    GRANT UPDATE (FLD_FOR_JUNIORS) ON TEST TO ROLE FLD_FOR_JUNIORS_UPDATER
    GRANT UPDATE (FLD_FOR_SENIORS) ON TEST TO ROLE FLD_FOR_SENIORS_UPDATER
    GRANT SELECT ON TEST TO PUBLIC
    GRANT FLD_FOR_JUNIORS_UPDATER TO JUNIOR_MNGR
    GRANT FLD_FOR_SENIORS_UPDATER TO SENIOR_MNGR

    USER                            BIG_BROTHER
    ROLE                            NONE
    FLD_FOR_SENIORS                 updated by BIG_BROTHER, role: NONE
    FLD_FOR_JUNIORS                 created by sysdba
    FLD_FOR_SENIORS                 updated by BIG_BROTHER, role: NONE
    FLD_FOR_JUNIORS                 created by sysdba

    USER                            SENIOR_MNGR
    ROLE                            FLD_FOR_SENIORS_UPDATER
    FLD_FOR_SENIORS                 updated by SENIOR_MNGR, role: FLD_FOR_SENIORS_UPDATER
    FLD_FOR_JUNIORS                 created by sysdba
    FLD_FOR_SENIORS                 updated by SENIOR_MNGR, role: FLD_FOR_SENIORS_UPDATER
    FLD_FOR_JUNIORS                 created by sysdba

    USER                            JUNIOR_MNGR
    ROLE                            FLD_FOR_JUNIORS_UPDATER
    FLD_FOR_SENIORS                 updated by SENIOR_MNGR, role: FLD_FOR_SENIORS_UPDATER
    FLD_FOR_JUNIORS                 created by sysdba
    FLD_FOR_SENIORS                 updated by SENIOR_MNGR, role: FLD_FOR_SENIORS_UPDATER
    FLD_FOR_JUNIORS                 updated by junior_mngr, role: fld_for_juniors_updater
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to COLUMN TEST.FLD_FOR_JUNIORS

    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to COLUMN TEST.FLD_FOR_JUNIORS

    Statement failed, SQLSTATE = 28000
    no permission for UPDATE access to COLUMN TEST.FLD_FOR_SENIORS
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action, user_a: User, user_b: User, user_c: User, role_a: Role, role_b: Role):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

