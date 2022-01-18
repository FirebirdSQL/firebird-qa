#coding:utf-8

"""
ID:          issue-965
ISSUE:       965
TITLE:       Tricky role defeats basic SQL security
DESCRIPTION:
JIRA:        CORE-606
"""

import pytest
from firebird.qa import *

substitutions = [('Statement failed, SQLSTATE = HY000', ''),
                   ('record not found for user:.*', ''), ('read/select', 'SELECT'),
                   ('Data source : Firebird::.*', 'Data source : Firebird::'),
                   ('-At block line: [\\d]+, col: [\\d]+', '-At block line'),
                   ('335545254 : Effective user is.*', '')]

db = db_factory()
for_cvc_role = role_factory('db', name='"FOR CVC"')
for_role = role_factory('db', name='"FOR"')
cvc_user = user_factory('db', name='cvc', password='pw')

test_script = """
    recreate table "t t"(data int);
    commit;
    insert into "t t" values(123456);
    commit;

    grant "FOR CVC" to user cvc;
    grant select on table "t t" to "FOR";
    commit;

    show grants;
    commit;

    set list on;
    set term ^;
    execute block returns(who_am_i varchar(31), i_m_playing_role varchar(31)) as
    begin
      for
         execute statement 'select current_user, current_role from rdb$database'
         on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
         as user 'cvc' password 'pw' role '"FOR CVC"'
         into who_am_i, i_m_playing_role
      do
         suspend;
    end
    ^

    execute block returns(data int) as
    begin
      for
         execute statement 'select data from "t t"'
         on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
         as user 'cvc' password 'pw' role '"FOR CVC"'
         into data
      do
         suspend;
    end
    ^
    set term ;^
    commit;

    --                                    ||||||||||||||||||||||||||||
    -- ###################################|||  FB 4.0+, SS and SC  |||##############################
    --                                    ||||||||||||||||||||||||||||
    -- If we check SS or SC and ExtConnPoolLifeTime > 0 (config parameter FB 4.0+) then current
    -- DB (bugs.core_NNNN.fdb) will be 'captured' by firebird.exe process and fbt_run utility
    -- will not able to drop this database at the final point of test.
    -- Moreover, DB file will be hold until all activity in firebird.exe completed and AFTER this
    -- we have to wait for <ExtConnPoolLifeTime> seconds after it (discussion and small test see
    -- in the letter to hvlad and dimitr 13.10.2019 11:10).
    -- This means that one need to kill all connections to prevent from exception on cleanup phase:
    -- SQLCODE: -901 / lock time-out on wait transaction / object <this_test_DB> is in use
    -- #############################################################################################
    delete from mon$attachments where mon$attachment_id != current_connection;
    commit;
"""

act = isql_act('db', test_script, substitutions=substitutions)

expected_stdout = """
/* Grant permissions for this database */
GRANT SELECT ON t t TO ROLE FOR
GRANT FOR CVC TO CVC

WHO_AM_I                        CVC
I_M_PLAYING_ROLE                FOR CVC
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    Execute statement error at isc_dsql_prepare :
    335544352 : no permission for SELECT access to TABLE t t
    Statement : select data from "t t"
    Data source : Firebird::localhost:C:\\FBTESTING\\QA\\FBT-REPO\\TMP\\E30.FDB
    -At block line: 3, col: 7
"""


@pytest.mark.version('>=3')
def test_1(act: Action, cvc_user: User, for_role: Role, for_cvc_role: Role):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

