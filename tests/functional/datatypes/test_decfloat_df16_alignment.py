#coding:utf-8
#
# id:           functional.datatypes.decfloat_df16_alignment
# title:        Check proper alignment of decfloat(16) value if it is shown in ISQL when SET LIST ON.
# decription:   
#                   See CORE-5535 and doc\\sql.extensions\\README.data_types
#                   Test is based on letter to Alex, 02.05.2017, 9:38: 
#                   For ISQL 'SET LIST ON' there was auxiliary ("wrong") space character between column name 
#                   for decfloat(16) and its value comparing with decfloat(34).
#                   FB40CS, build 4.0.0.651: OK, 1.406ss.
#                 
# tracker_id:   
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    recreate table test(
         a varchar(1) default '|'
        ,x34 decfloat(34) default -9.999999999999999999999999999999999E6144
        ,y16 decfloat(16) default -9.999999999999999E384
        ,u34 decfloat(34) default 9.999999999999999999999999999999999E6144
        ,v16 decfloat(16) default 9.999999999999999E384
        ,w varchar(1) default '|'
    );
    commit;
    insert into test default values returning a,x34,y16,u34,v16,w;
   """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A                               |
    X34                             -9.999999999999999999999999999999999E+6144
    Y16                             -9.999999999999999E+384
    U34                              9.999999999999999999999999999999999E+6144
    V16                              9.999999999999999E+384
    W                               |
 """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

