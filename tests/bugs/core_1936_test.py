#coding:utf-8
#
# id:           bugs.core_1936
# title:        The log(base, number) built-in function doesn't check parameters and delivers NAN values instead.
# decription:   
# tracker_id:   CORE-1936
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select log(2, 00) from rdb$database;
select log(2, -2) from rdb$database;
select log(0, 1) from rdb$database;
select log(0, 2) from rdb$database;
select log(-1, 2) from rdb$database;
select log(-1, 0) from rdb$database;
select log(-1, -1) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
                    LOG
=======================

                    LOG
=======================

                    LOG
=======================

                    LOG
=======================

                    LOG
=======================

                    LOG
=======================

                    LOG
=======================
"""
expected_stderr_1 = """Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Argument for LOG must be positive

Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Argument for LOG must be positive

Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Base for LOG must be positive

Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Base for LOG must be positive

Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Base for LOG must be positive

Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Base for LOG must be positive

Statement failed, SQLSTATE = 42000

expression evaluation not supported

-Base for LOG must be positive

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout

