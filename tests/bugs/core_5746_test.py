#coding:utf-8

"""
ID:          issue-2171
ISSUE:       2171
TITLE:       Remove the restriction on create/delete, enable/disable the user indexes in system tables
DESCRIPTION:
  Test verifies that one may to:
    * create two indices (common and calculated) and
    * gather statistics on them
    * make some of them inactive and return then to active state
    * drop them.
  This is checked first under SYSDBA account, then under common non-privileged user (and these attempts should raise exception)
  and finally we grant DDL privilege to this user (ALTER ANY TABLE) and check again, and this should pass OK.

  Restictions about create/alter/drop indexes on system tables that are checked by test for CORE-4731 should be removed.
JIRA:        CORE-5746
FBTEST:      bugs.core_5746
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
      set list on;
      set plan on;
      create descending index systable_comm_idx on rdb$relations(rdb$format);
      create descending index systable_calc_idx on rdb$relations computed by ( 1 + rdb$format );
      set statistics index systable_comm_idx;
      set statistics index systable_calc_idx;

      select sign(count(*)) as sign_count from rdb$relations where rdb$format < 65537;
      select sign(count(*)) as sign_count from rdb$relations where 1 + rdb$format < 65537;

      alter index systable_calc_idx inactive;
      alter index systable_calc_idx active;

      drop index systable_comm_idx;
      drop index systable_calc_idx;
      commit;

      create or alter user tmp$c5746 password '123';
      commit;

      connect '$(DSN)' user tmp$c5746 password '123';
      -- this should FAIL:
      create descending index systable_comm_idx on rdb$relations(rdb$format);
      commit;


      connect '$(DSN)' user 'SYSDBA' password 'masterkey';
      grant alter any table to tmp$c5746;
      commit;


      connect '$(DSN)' user tmp$c5746 password '123';
      -- All following statements should PASS:
      create descending index systable_comm_idx on rdb$relations(rdb$format);
      create descending index systable_calc_idx on rdb$relations computed by ( 1 + rdb$format );
      set statistics index systable_comm_idx;
      set statistics index systable_calc_idx;

      select sign(count(*)) as sign_count from rdb$relations where rdb$format < 65537;
      select sign(count(*)) as sign_count from rdb$relations where 1 + rdb$format < 65537;

      alter index systable_calc_idx inactive;
      alter index systable_calc_idx active;

      drop index systable_comm_idx;
      drop index systable_calc_idx;
      commit;


      connect '$(DSN)' user 'SYSDBA' password 'masterkey';
      drop user tmp$c5746;
      commit;

"""

act = isql_act('db', test_script, substitutions=[('-Effective user is.*', '')])

expected_stdout = """
    PLAN (RDB$RELATIONS INDEX (SYSTABLE_COMM_IDX))
    SIGN_COUNT                      1
    PLAN (RDB$RELATIONS INDEX (SYSTABLE_CALC_IDX))
    SIGN_COUNT                      1

    PLAN (RDB$RELATIONS INDEX (SYSTABLE_COMM_IDX))
    SIGN_COUNT                      1
    PLAN (RDB$RELATIONS INDEX (SYSTABLE_CALC_IDX))
    SIGN_COUNT                      1
"""

expected_stderr = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE INDEX SYSTABLE_COMM_IDX failed
    -no permission for ALTER access to TABLE RDB$RELATIONS
"""

@pytest.mark.version('>=3.0.4')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

