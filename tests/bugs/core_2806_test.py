#coding:utf-8
#
# id:           bugs.core_2806
# title:        Views based on procedures can't be created if the proc's output fields participate in an expression
# decription:   
# tracker_id:   CORE-2806
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """set term ^;
create procedure p returns(rc int) as begin rc = 1; suspend; end^
create view v2(dosrc) as select rc * 2 from p^
commit ^
show view v2^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """DOSRC                           BIGINT Expression
View Source:
==== ======
 select rc * 2 from p
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

