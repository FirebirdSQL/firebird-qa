#coding:utf-8

"""
ID:          issue-4403
ISSUE:       4403
TITLE:       Server bugchecks or crashes on exception in calculated index
DESCRIPTION:
NOTES:
[18.10.2016] added test case from #4918
  NB: 2.5.x output contains TWO lines with error message, i.e.:
    Statement failed, SQLSTATE = 22018
    conversion error from string "2014.02.33"
    -conversion error from string "2014.02.33"
  Decided to suppress second line because its unlikely to be fixed
  (after get reply from dimitr, letter 18.10.2016 18:47).
[16.09.2017] added separate section for 4.0 because STDERR now
  contains name of index that causes problem - this is so after core-5606
  was implemented ("Add expression index name to exception message ...")
JIRA:        CORE-4075
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table TEST (BIT smallint);
    create index IDX_TEST_BIT on TEST computed by (bin_shl(1, TEST.BIT-1));

    -- from CORE-4603:
    recreate table T_TABLE (
        F_YEAR varchar(4),
        F_MONTH_DAY varchar(5)
    );
    create index T_INDEX on T_TABLE computed by (cast(F_YEAR || '.' || F_MONTH_DAY as date));
    commit;

  """

db = db_factory(init=init_script)

test_script = """
    insert into test values (0);
    -- Trace:
    -- 335544606 : expression evaluation not supported
    -- 335544967 : Argument for BIN_SHL must be zero or positive

    -- from core-4603:
    insert into T_TABLE (F_YEAR, F_MONTH_DAY) values ('2014', '02.33');
"""

act = isql_act('db', test_script, substitutions=[('-conversion error from string "2014.02.33"', '')])

# version: 3

expected_stderr_1 = """
    Statement failed, SQLSTATE = 42000
    expression evaluation not supported
    -Argument for BIN_SHL must be zero or positive

    Statement failed, SQLSTATE = 22018
    conversion error from string "2014.02.33"
"""

@pytest.mark.version('>=3,<4.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr_1
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

# version: 4.0

expected_stderr_2 = """
    Statement failed, SQLSTATE = 42000
    Expression evaluation error for index "IDX_TEST_BIT" on table "TEST"
    -expression evaluation not supported
    -Argument for BIN_SHL must be zero or positive

    Statement failed, SQLSTATE = 22018
    Expression evaluation error for index "T_INDEX" on table "T_TABLE"
    -conversion error from string "2014.02.33"
"""

@pytest.mark.version('>=4.0')
def test_2(act: Action):
    act.expected_stderr = expected_stderr_2
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

