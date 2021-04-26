#coding:utf-8
#
# id:           bugs.core_6479
# title:        COMMENT ON USER can only apply comment on user defined by the default usermanager plugin
# decription:   
#                   ::: NOTE :::
#                   There is no sense to check for Legacy_UserManarer: comment for user will not be stored in the sec$users for this plugin.
#                   Test verifies only Srp. Discussed with Alex, 12.03.2021
#               
#                   Checked on: 4.0.02386, 3.0.8.33425
#                
# tracker_id:   CORE-6479
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = [('SEC_DESCR_BLOB_ID .*', ''), ('[\t ]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter user tmp$c6479_srp password '123' using plugin Srp;
    commit;
    comment on user tmp$c6479_srp using plugin Srp is 'This is description for Srp-user';
    --                            ================
    commit;

    set list on;
    set count on;
    select s.sec$user_name, s.sec$plugin, s.sec$description as sec_descr_blob_id
    from sec$users s
    where s.sec$user_name  = upper('tmp$c6479_srp')
    ;
    drop user tmp$c6479_srp using plugin Srp;
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SEC$USER_NAME                   TMP$C6479_SRP
    SEC$PLUGIN                      Srp
    This is description for Srp-user
    Records affected: 1
  """

@pytest.mark.version('>=3.0.8')
def test_core_6479_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

