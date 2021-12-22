#coding:utf-8
#
# id:           bugs.core_2315
# title:        Firebird float support does not conform to Interbase spec
# decription:   
# tracker_id:   CORE-2315
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """create table float_test (i integer, f float);
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """insert into float_test values (1, 3.0);
insert into float_test values (1, 3.402823466e+38);
select * from float_test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           I              F
============ ==============
           1      3.0000000
           1  3.4028235e+38

"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

