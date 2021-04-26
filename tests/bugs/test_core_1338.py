#coding:utf-8
#
# id:           bugs.core_1338
# title:        Problem with view , computed field and functions
# decription:   
# tracker_id:   CORE-1338
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1338

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """create table a (a numeric(15,15));

insert into a values(2);

create view b(a) as select round(a,2) from a;

select * from b;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                    A
=====================
    2.000000000000000

"""

@pytest.mark.version('>=2.1')
def test_core_1338_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

