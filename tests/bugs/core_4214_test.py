#coding:utf-8
#
# id:           bugs.core_4214
# title:        GTT should not reference permanent relation
# decription:   
# tracker_id:   CORE-4214
# min_versions: ['2.5.3']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set autoddl off; 
    commit;
    create global temporary table gtt_main(x int, y int, constraint gtt_main_unq unique(x,y) using index gtt_main_unq);
    create table fix_main(x int, y int, constraint fix_main_unq unique(x,y) using index fix_main_unq);
    create global temporary table gtt_detl(x int, y int, 
      constraint gtt_detl_fk_to_gtt foreign key(x,y) references gtt_main(x, y), 
      constraint gtt_detl_fk_to_fix foreign key(x,y) references fix_main(x, y) 
    );
    create table fix_detl(x int, y int, 
      constraint fix_detl_fk_to_fix foreign key(x,y) references fix_main(x, y), 
      constraint fix_detl_fk_to_gtt foreign key(x,y) references gtt_main(x, y) 
    );
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    unsuccessful metadata update
    -CREATE TABLE GTT_DETL failed
    -global temporary table "GTT_DETL" of type ON COMMIT DELETE ROWS cannot reference persistent table "FIX_MAIN"
    Statement failed, SQLSTATE = HY000
    unsuccessful metadata update
    -CREATE TABLE FIX_DETL failed
    -persistent table "FIX_DETL" cannot reference global temporary table "GTT_MAIN" of type ON COMMIT DELETE ROWS
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

