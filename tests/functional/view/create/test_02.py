#coding:utf-8

"""
ID:          view.create-02
TITLE:       CREATE VIEW
DESCRIPTION:
FBTEST:      functional.view.create.02
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE tb(id INT);
commit;
"""

db = db_factory(init=init_script)

test_script = """CREATE VIEW test (id,num) AS SELECT id,5 FROM tb;
SHOW VIEW test;
"""

act = isql_act('db', test_script)

expected_stdout = """ID                              INTEGER Nullable
NUM                             INTEGER Expression
View Source:
==== ======
SELECT id,5 FROM tb
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
