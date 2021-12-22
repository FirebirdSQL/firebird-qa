#coding:utf-8
#
# id:           bugs.core_0903
# title:        New value of column is accessable before update
# decription:   
# tracker_id:   CORE-903
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TEST (
    T1 INTEGER,
    T2 INTEGER,
    T3 INTEGER,
    T4 INTEGER
);

Insert into test (T1, T2, T3, T4) values ( 0, 0 , 0, 0);

SET TERM ^ ;

CREATE OR ALTER PROCEDURE CH_TEST (
    num integer)
as
begin

update TEST
 set
   T1= T1 + T2 + T3 + T4 + :NUM
   ,T2= T1 + T2 + T3 + T4 + :NUM
   ,T3= T1 + T2 + T3 + T4 + :NUM
   ,T4= T1 + T2 + T3 + T4 + :NUM
 ;

end^

SET TERM ; ^
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """execute procedure ch_test( 1 );
select * from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          T1           T2           T3           T4
============ ============ ============ ============
           1            1            1            1

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

