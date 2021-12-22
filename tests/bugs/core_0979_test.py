#coding:utf-8
#
# id:           bugs.core_0979
# title:        Make RDB$DB_KEY in outer joins return NULL when appropriate
# decription:   ----------------------------------------------------------------------------------------------
#               -- test de la fonctionalité
#               --
#               --
#               --Make RDB$DB_KEY in outer joins return NULL when appropriate
#               --A. dos Santos Fernandes
#               --Feature request CORE-979
# tracker_id:   CORE-979
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_979

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE employee( id_employee INTEGER , prenom VARCHAR(20) ,id_department INTEGER, PRIMARY KEY(id_employee));
CREATE TABLE department(id_department INTEGER, name VARCHAR(20));
COMMIT;
INSERT INTO employee(id_employee, prenom,id_department) VALUES (1,'benoit',1 );
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select department.rdb$db_key  from employee
left OUTER JOIN department
 on department.id_department = employee.id_department;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """DB_KEY
================
<null>"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

