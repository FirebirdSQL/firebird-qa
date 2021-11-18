#coding:utf-8
#
# id:           bugs.core_4205
# title:        ISQL -x does not output the START WITH clause of generators/sequences
# decription:
# tracker_id:   CORE-4205
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('^((?!CREATE GENERATOR).)*$', '')]

init_script_1 = """
    recreate sequence tmp_gen_42051 start with 9223372036854775807 increment by -2147483647;
    recreate sequence tmp_gen_42052 start with -9223372036854775808 increment by 2147483647;
    recreate sequence tmp_gen_42053 start with 9223372036854775807 increment by  2147483647;
    recreate sequence tmp_gen_42054 start with -9223372036854775808 increment by -2147483647;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# db_conn.close()
#  runProgram('isql',[dsn,'-x','-user',user_name,'-password',user_password])
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    CREATE GENERATOR TMP_GEN_42051 START WITH 9223372036854775807 INCREMENT -2147483647;
    CREATE GENERATOR TMP_GEN_42052 START WITH -9223372036854775808 INCREMENT 2147483647;
    CREATE GENERATOR TMP_GEN_42053 START WITH 9223372036854775807 INCREMENT 2147483647;
    CREATE GENERATOR TMP_GEN_42054 START WITH -9223372036854775808 INCREMENT -2147483647;
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=['-x'])
    assert act_1.clean_stdout == act_1.clean_expected_stdout


