#coding:utf-8
#
# id:           functional.dml.join.02
# title:        NATURAL join
# decription:   <natural join> ::=
#               <table reference> NATURAL <join type> JOIN <table primary>
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.dml.join.join_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE employee( id_employee INTEGER , prenom VARCHAR(20) ,id_department INTEGER, PRIMARY KEY(id_employee));
CREATE TABLE department(id_department INTEGER, name VARCHAR(20));
INSERT INTO department(id_department, name) values(1,'somme');
INSERT INTO department(id_department, name) values(2,'pas de calais');
INSERT INTO employee(id_employee, prenom,id_department) VALUES (1,'benoit',1 );
INSERT INTO employee(id_employee, prenom,id_department) VALUES (2,'tom',2 );"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select employee.prenom , department.name from employee natural join department;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PRENOM               NAME
==================== ====================
benoit               somme
tom                  pas de calais
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

