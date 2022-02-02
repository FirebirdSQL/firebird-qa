#coding:utf-8

"""
ID:          issue-3179
ISSUE:       3179
TITLE:       isql extracts the array dimensions after the character set name
DESCRIPTION:
JIRA:        CORE-2788
FBTEST:      bugs.core_2788
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('- line .*', ''), ('At line .*', '')])

sql_ddl = """
create domain dm_test as char(1) character set iso8859_1[1:2];
create domain dm_test as char(1)[1:2] character set iso8859_1;
commit;
show domain dm_test;
"""

expected_stdout = """
    DM_TEST                         ARRAY OF [2]
    CHAR(1) CHARACTER SET ISO8859_1 Nullable
"""

expected_stderr_a = """
    Statement failed, SQLSTATE = 42000
    Dynamic SQL Error
    -SQL error code = -104
    -Token unknown - line 1, column 57
    -[
"""

expected_stderr_b = """
   There is no domain DM_TEST in this database
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr_a
    act.expected_stdout = expected_stdout
    act.isql(switches=[], input=sql_ddl)
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
    #
    act.reset()
    act.isql(switches=['-x'])
    xmeta = act.stdout
    #
    with act.db.connect() as con:
        c = con.cursor()
        c.execute('drop domain dm_test')
        con.commit()
    #
    act.reset()
    act.expected_stderr = expected_stderr_b
    act.isql(switches=['-q'], input='show domain dm_test;')
    assert act.clean_stderr == act.clean_expected_stderr
    #
    act.reset()
    act.isql(switches=[], input=xmeta)
    #
    act.reset()
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input='show domain dm_test;')
    assert act.clean_stdout == act.clean_expected_stdout
