#coding:utf-8
#
# id:           functional.intfunc.math.rand_01
# title:        test for RAND function
# decription:   
#                 RAND()
#                 Returns a random number between 0 and 1.
# tracker_id:   
# min_versions: []
# versions:     3.0
# qmid:         functional.intfunc.math.rand_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create table test( id char(30) );

--on verrifie qu'il y en a pas deux identique
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );
insert into test values(CAST(rand() AS VARCHAR(255)) );


select count(id)  from test group by id;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                COUNT
=====================
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1
                    1

"""

@pytest.mark.version('>=3.0')
def test_rand_01_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

