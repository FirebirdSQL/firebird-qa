#coding:utf-8
#
# id:           bugs.gh_5082
# title:        Exception "too few key columns found for index" raises when attempt to create table with PK and immediatelly drop this PK within the same transaction [CORE4783]
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/5082
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
    commit;
    --set echo on;
    create table test(
         f01 varchar(2)
        ,constraint test_pk1 primary key (f01)
    );
    alter table test drop constraint test_pk1;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.execute()
