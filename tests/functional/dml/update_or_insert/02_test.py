#coding:utf-8
#
# id:           functional.dml.update_or_insert.02
# title:        UPDATE OR INSERT
# decription:   WITH RETURNING Clause
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.dml.update_or_insert.update_or_insert_02

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TMPTEST( id INTEGER , name VARCHAR(20) , PRIMARY KEY(id));"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^ ;

EXECUTE BLOCK
RETURNS (V integer)
AS

  BEGIN
	UPDATE OR INSERT INTO TMPTEST(id, name) VALUES (1,'ivan' )
	RETURNING id INTO :V;
	SUSPEND;

  END^


SET TERM ; ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
           V
============
           1

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

