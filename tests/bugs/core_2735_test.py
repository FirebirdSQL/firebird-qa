#coding:utf-8
#
# id:           bugs.core_2735
# title:        isql hangs when trying to show a view based on a procedure
# decription:   
# tracker_id:   CORE-2735
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """set term ^;
create procedure p returns(a int) as begin a = 9; suspend; end^
create view vp1 as select a from p^
set term ;^
COMMIT;"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """show view vp1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """A                               INTEGER Nullable
View Source:
==== ======
 select a from p
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

