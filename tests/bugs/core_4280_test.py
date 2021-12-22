#coding:utf-8
#
# id:           bugs.core_4280
# title:        FB3: Stored function accepts duplicate input arguments
# decription:   
#                    02.02.2019. Replaced 'show func' with query to RDB$FUNCTIONS table: we have just to ensure that no function did appear in DB.
#                    (removed 'show func' because its output is mutable and can be directed either to STDERR or STDOUT in diff. FB versions).
#                    Checked on:
#                       4.0.0.1421: OK, 1.512s.
#                       3.0.5.33097: OK, 0.907s.
#                       3.0.2.32658: OK, 0.840s.
#                       3.0.4.33054: OK, 1.368s.
#                
# tracker_id:   CORE-4280
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create view v_check as
    select 
        rf.rdb$function_name as func_name
       ,rf.rdb$legacy_flag as legacy_flag
    from rdb$functions rf where rf.rdb$function_name = upper('psql_func_test')
    ;
    commit;

    set term ^;
    create function psql_func_test(x integer, y boolean, x integer) -- argument `x` appears twice 
    returns integer as
    begin
        return x + 1;
    end 
    ^
    set term ;^
    commit;
    
    set list on;
    set count on;
    select * from v_check;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    CREATE FUNCTION PSQL_FUNC_TEST failed
    -SQL error code = -901
    -duplicate specification of X - not supported
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

