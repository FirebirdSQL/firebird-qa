#coding:utf-8
#
# id:           bugs.core_3256
# title:        Error "request depth exceeded" may appear while preparing a select query against a view with explicit plan
# decription:   
# tracker_id:   CORE-3256
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter view vt(id,name) as select 1 id, '' name from rdb$database;
    commit;
    
    recreate table t1 (id integer not null,name integer not null);
    alter table t1 add constraint pk_t1 primary key (id)  
    using index pk_t1
    ;
    create or alter view vt(id,name) as select * from t1;
    commit;

    -- repeat ~130 times
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    ---
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    
    -- The following statement leads to:
    -- Statement failed, SQLSTATE = 54001
    -- unsuccessful metadata update
    -- -request depth exceeded. (Recursive definition?)
    -- Confirmed for 2.5.0 only, 26.02.2015.
    --#####################################################
    select * from vt where id=1 PLAN (vt T1 INDEX (PK_T1));
    --#####################################################
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.execute()

