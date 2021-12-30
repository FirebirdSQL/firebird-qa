#coding:utf-8
#
# id:           bugs.gh_5173
# title:        Compound ALTER TABLE statement with ADD and DROP the same constraint failed if this constraint involves index creation (PK/UNQ/FK) [CORE4878]
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/5173
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
    recreate table t1(x int not null);
    recreate table t2(x int not null);
    recreate table t3(x int not null);

    -- set echo on;

    alter table t1 add constraint t1_unq unique(x), drop constraint t1_unq;

    alter table t2 add constraint t2_pk primary key(x), drop constraint t2_pk;

    alter table t3 add constraint t3_pk primary key(x), add constraint t3_fk foreign key(x) references t3(x), drop constraint t3_fk;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.execute()
