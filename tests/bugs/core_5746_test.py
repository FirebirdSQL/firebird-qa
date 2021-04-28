#coding:utf-8
#
# id:           bugs.core_5746
# title:        Remove the restriction on create/delete, enable/disable the user indexes in system tables
# decription:   
#                  Test verifies that one may to:
#                    * create two indices (common and calculated) and 
#                    * gather statistics on them
#                    * make some of them inactive and return then to active state
#                    * drop them.
#                  This is checked first under SYSDBA account, then under common non-privileged user (and these attempts should raise exception)
#                  and finally we grant DDL privilege to this user (ALTER ANY TABLE) and check again, and this should pass OK.
#               
#                  ::: NB :::
#                 
#                  Restictions about create/alter/drop indexes on system tables that are checked by test for CORE-4731 should be removed.
#               
#                  Checked on:
#                   3.0.4.32944: OK, 1.500s.
#                   4.0.0.952: OK, 1.079s.
#                
# tracker_id:   CORE-5746
# min_versions: ['3.0.4']
# versions:     3.0.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.4
# resources: None

substitutions_1 = [('-Effective user is.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PLAN (RDB$RELATIONS INDEX (SYSTABLE_COMM_IDX))
    SIGN_COUNT                      1
    PLAN (RDB$RELATIONS INDEX (SYSTABLE_CALC_IDX))
    SIGN_COUNT                      1

    PLAN (RDB$RELATIONS INDEX (SYSTABLE_COMM_IDX))
    SIGN_COUNT                      1
    PLAN (RDB$RELATIONS INDEX (SYSTABLE_CALC_IDX))
    SIGN_COUNT                      1
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -CREATE INDEX SYSTABLE_COMM_IDX failed
    -no permission for ALTER access to TABLE RDB$RELATIONS
  """

@pytest.mark.version('>=3.0.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

