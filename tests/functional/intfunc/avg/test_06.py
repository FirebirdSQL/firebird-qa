#coding:utf-8

"""
ID:          intfunc.avg-06
TITLE:       AVG - Integer OverFlow
DESCRIPTION:
NOTES:
[14.10.2019] Refactored: adjusted expected_stdout/stderr
[25.06.2020] 4.0.0.2076: changed types in SQLDA from numeric to int128 // after discuss with Alex about CORE-6342.
[09.07.2020], 4.0.0.2091:
  NO more overflow since INT128 was introduced. AVG() is evaluated successfully.
  Removed error message from expected_stderr, added result into expected_stdout.
[27.07.2021] changed sqltype in FB 4.x+ to 580 INT64: this is needed since fix #6874.
FBTEST:      functional.intfunc.avg.06
"""

import pytest
from firebird.qa import *

init_script = """
    recreate table test( id integer not null);
    insert into test values(2100000000);
    insert into test values(2100000000);
    insert into test values(2100000000);
    insert into test values(2100000000);
    commit;
    create or alter view v_test as select avg(2100000000*id)as avg_result from test;
    commit;
"""

db = db_factory(init=init_script)

test_script = """
    set list on;
    set sqlda_display on;
    select * from v_test;
"""

act = isql_act('db', test_script, substitutions=[('^((?!sqltype|AVG_RESULT).)*$', ''), ('[ \t]+', ' ')])

# version: 3.0

expected_stdout_1 = """
    INPUT message field count: 0
    OUTPUT message field count: 1
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
    : name: AVG_RESULT alias: AVG_RESULT
    : table: V_TEST owner: SYSDBA
"""

expected_stderr_1 = """
    Statement failed, SQLSTATE = 22003
    Integer overflow.  The result of an integer operation caused the most significant bit of the result to carry.
"""

@pytest.mark.version('>=3.0,<4.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout_1
    act.expected_stderr = expected_stderr_1
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

# version: 4.0

expected_stdout_2 = """
      01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
      :  name: AVG_RESULT  alias: AVG_RESULT
      : table: V_TEST  owner: SYSDBA

    AVG_RESULT                                                4410000000000000000
"""

@pytest.mark.version('>=4.0')
def test_2(act: Action):
    act.expected_stdout = expected_stdout_2
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
