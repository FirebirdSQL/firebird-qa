#coding:utf-8

"""
ID:          view.create-01
TITLE:       CREATE VIEW
DESCRIPTION:
FBTEST:      functional.view.create.01
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE tb(id INT);
commit;
"""

db = db_factory(init=init_script)

test_script = """CREATE VIEW test AS SELECT * FROM tb;
SHOW VIEW test;
"""

act = isql_act('db', test_script)

expected_stdout = """ID                              INTEGER Nullable
View Source:
==== ======
SELECT * FROM tb
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
