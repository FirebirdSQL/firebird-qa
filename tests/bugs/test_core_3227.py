#coding:utf-8
#
# id:           bugs.core_3227
# title:        ASCII_VAL() fails if argument contains multi-byte character anywhere
# decription:   
# tracker_id:   CORE-3227
# min_versions: ['2.1.4']
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """select ascii_val (cast('Hoplala' as char(12) character set utf8)) from rdb$database;
select ascii_val (cast('Hopläla' as char(12) character set utf8)) from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
ASCII_VAL
=========
       72


ASCII_VAL
=========
       72

"""

@pytest.mark.version('>=2.1.4')
def test_core_3227_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

