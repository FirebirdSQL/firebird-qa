#coding:utf-8
#
# id:           bugs.gh_6825
# title:        Correct error message for DROP VIEW
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6825
#               
#                   Confirmed issue on 5.0.0.56, 4.0.0.2468.
#                   Checked on 5.0.0.60, 4.0.0.2502, 3.0.8.33470 -- all OK.
#                
# tracker_id:   
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = [('(-)?Effective user is.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate view v1 as select 1 x from rdb$database;
    create or alter user tmp$gh_6825 password '123' using plugin Srp;
    commit;
    connect '$(DSN)' user tmp$gh_6825 password '123';
    drop view v1;
    commit;
    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$gh_6825 using plugin Srp;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -DROP VIEW V1 failed
    -no permission for DROP access to VIEW V1
    -Effective user is TMP$GH_6825
"""

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
