#coding:utf-8

"""
ID:          view.create-08
TITLE:       CREATE VIEW - updateable WITH CHECK OPTION
DESCRIPTION:
FBTEST:      functional.view.create.08
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE tb(id INT);
commit;
"""

db = db_factory(init=init_script)

test_script = """CREATE VIEW test (id) AS SELECT id FROM tb WHERE id<10 WITH CHECK OPTION;
INSERT INTO test VALUES(10);
"""

act = isql_act('db', test_script, substitutions=[('-At trigger.*', '')])

expected_stderr = """Statement failed, SQLSTATE = 23000
Operation violates CHECK constraint  on view or table TEST
-At trigger 'CHECK_1'
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
