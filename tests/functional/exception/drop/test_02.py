#coding:utf-8

"""
ID:          exception.drop-02
FBTEST:      functional.exception.drop.02
TITLE:       DROP EXCEPTION
DESCRIPTION:
  Create exception and SP that uses it. Then try to drop exception - this attempt must FAIL.
"""

import pytest
from firebird.qa import *

init_script = """
    create exception exc_test 'message to show';
    commit;
    set term ^;
    create procedure sp_test as
    begin
      exception exc_test;
    end ^
    set term ;^
    commit;
  """

db = db_factory(init=init_script)

test_script = """
    drop exception exc_test;
    commit;
    set list on;
    set count on;
    select e.rdb$exception_name, d.rdb$dependent_name
    from rdb$exceptions e join rdb$dependencies d on e.rdb$exception_name = d.rdb$depended_on_name
    where e.rdb$exception_name = upper('exc_test');
"""

act = isql_act('db', test_script)

expected_stdout = """
    RDB$EXCEPTION_NAME              EXC_TEST
    RDB$DEPENDENT_NAME              SP_TEST
    Records affected: 1
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -cannot delete
    -EXCEPTION EXC_TEST
    -there are 1 dependencies
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
