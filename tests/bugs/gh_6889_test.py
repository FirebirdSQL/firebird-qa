#coding:utf-8
#
# id:           bugs.gh_6889
# title:        error no permision occurred while ALTER USER SET TAGS on snapshot build WI-V3.0.8.33482
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6889
#               
#                   Checked on:
#                       5.0.0.113;   5.0.0.88
#                       4.0.1.2539;  4.0.1.2523
#                       3.0.8.33487; 3.0.8.33476
#                
# tracker_id:   
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter user tmp$gh_6889 password '123' using plugin Srp;
    commit;

    connect '$(DSN)' user tmp$gh_6889 password '123';
    alter current user set tags ( active2 = 'TRUE' );
    commit;

    connect '$(DSN)' user sysdba password 'masterkey';
    drop user tmp$gh_6889 using plugin Srp;
    commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
