# coding:utf-8

"""
ID:          functional.tablespace.ts_comment
TITLE:       Test the ability to comment on tablespaces
DESCRIPTION:
"""

import pytest
from firebird.qa import *

init_script = """
CREATE TABLESPACE TS1 FILE './test_ts_comment.dat';
"""
db = db_factory(init=init_script)
act = isql_act('db')

expected_stdout = """
COMMENT ON TABLESPACE   TS1 IS Testing ts comment.;

Statement failed, SQLSTATE = 42000
unsuccessful metadata update
-COMMENT ON "TS2" failed
-Tablespace "TS2" not found

There are no comments for objects in this database
"""


@pytest.mark.version('>=6.0')
def test_1(act: Action):

    script = """
    COMMENT ON TABLESPACE TS1 IS 'Testing ts comment.';
    SHOW COMMENTS;

    COMMENT ON TABLESPACE TS2 IS 'Testing ts comment.';

    COMMENT ON TABLESPACE TS1 IS NULL;
    SHOW COMMENTS;
    """
    act.isql(switches=['-q'], input=script, combine_output=True)

    act.expected_stdout = expected_stdout
    assert act.clean_stdout == act.clean_expected_stdout
