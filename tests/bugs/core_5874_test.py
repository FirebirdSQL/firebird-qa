#coding:utf-8
#
# id:           bugs.core_5874
# title:        Provide name of read-only column incorrectly referenced in UPDATE ... SET xxx
# decription:   
#                  Table with computed field (non-ascii) that is result of addition is used here.
#                  UPDATE statement is used in trivial form, then as 'update or insert' and as 'merge'.
#                  All cases should produce STDERR with specifying table name and R/O column after dot.
#                  Checked on 4.0.0.1142: OK, 2.359s.
#                
# tracker_id:   CORE-5874
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test(id int, x int, y int, "hozzáadása" computed by (x * y) );
    commit;

    set planonly;

    update test set "hozzáadása" = 1;

    update or insert into test(id, "hozzáadása") 
    values(1, 111) matching(id)
    returning "hozzáadása";

    merge into test t
    using( select 1 as id, 2 as x, 3 as y from rdb$database ) s on s.id = t.id
    when matched then 
        update set "hozzáadása" = 1
    ;  
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    attempted update of read-only column TEST.hozzáadása

    Statement failed, SQLSTATE = 42000
    attempted update of read-only column TEST.hozzáadása

    Statement failed, SQLSTATE = 42000
    attempted update of read-only column TEST.hozzáadása
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

