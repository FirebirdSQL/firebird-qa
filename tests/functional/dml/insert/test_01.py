#coding:utf-8
#
# id:           functional.dml.insert.01
# title:        INSERT with Defaults
# decription:   INSERT INTO <table>
#               DEFAULT VALUES
#               [RETURNING <values>]
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.dml.insert.insert_01

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE employee( prenom VARCHAR(20) default 'anonymous' , sex CHAR(1) default 'M' );"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """insert into employee DEFAULT VALUES;
commit;
SELECT * FROM EMPLOYEE;
insert into employee DEFAULT VALUES RETURNING prenom,sex;
SELECT * FROM EMPLOYEE;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PRENOM               SEX
==================== ======
anonymous            M


PRENOM               SEX
==================== ======
anonymous            M


PRENOM               SEX
==================== ======
anonymous            M
anonymous            M
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

