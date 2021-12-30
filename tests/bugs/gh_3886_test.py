#coding:utf-8
#
# id:           bugs.gh_3886
# title:        recreate table T with PK or UK is impossible after duplicate typing w/o commit when ISQL is launched in AUTODDL=OFF mode [CORE3529]
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/3886
#               
#                   Checked on 5.0.0.271; 4.0.1.2637; 3.0.8.33524.
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
    set autoddl off;
    --set echo on;
    recreate table t(id int primary key);
    recreate table t(id int primary key);
    commit; 
    commit; -- yes, 2nd time.
    exit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.execute()
