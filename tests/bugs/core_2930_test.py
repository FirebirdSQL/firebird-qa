#coding:utf-8
#
# id:           bugs.core_2930
# title:        DROP VIEW drops output parameters of used stored procedures
# decription:   
# tracker_id:   CORE-2930
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """set term !;
create procedure p1 returns (n integer) as begin suspend; end!
create view v1 as select * from p1!
commit!
set term ;!
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """show procedure p1;
drop view v1;
show procedure p1;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Procedure text:
=============================================================================
 begin suspend; end
=============================================================================
Parameters:
N                                 OUTPUT INTEGER
Procedure text:
=============================================================================
 begin suspend; end
=============================================================================
Parameters:
N                                 OUTPUT INTEGER
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

