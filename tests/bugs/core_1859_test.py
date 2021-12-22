#coding:utf-8
#
# id:           bugs.core_1859
# title:        Arithmetic overflow or division by zero has occurred. in MAX function
# decription:   
#                    It was found that error raises in 2.1.0.17798 when we create table with two fields
#                    of UNICODE_FSS type and add there six rows. Content of fields were taken from table
#                    rdb$procedure_parameters of empty database.
#                    Data that are inserted have been found after several simplifications of source DB.
#                    Exception that raised:
#                    ===
#                        Statement failed, SQLCODE = -802
#                        arithmetic exception, numeric overflow, or string truncation
#                    ===
#                    Checked on: 
#                       2.1.1.17910 -- no error.
#                       2.5.9.27126: OK, 0.672s.
#                       3.0.5.33086: OK, 1.343s.
#                       4.0.0.1378: OK, 5.797s.
#                
# tracker_id:   CORE-1859
# min_versions: ['2.1.7']
# versions:     2.1.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test( param_name rdb$parameter_name, proc_name rdb$procedure_name );
    commit;
    insert into test values('A1',  'ABCDEFGHIJK');
    insert into test values('A',   'ASDFGHJKL');
    commit;

    set list on;
    set count on;
    select sign(count(*))
    from ( 
        select t.param_name, max( t.proc_name ) pnmax 
        from 
        ( select t.param_name, t.proc_name from test t rows 6 ) t
        group by 1
    );
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SIGN                            1
    Records affected: 1
"""

@pytest.mark.version('>=2.1.7')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

