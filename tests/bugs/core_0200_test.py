#coding:utf-8
#
# id:           bugs.core_0200
# title:        Empty column names with aggregate funcs
# decription:   
# tracker_id:   CORE-200
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_200

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select (select count(1) from rdb$database) from rdb$database ;
select (select avg(1) from rdb$database) from rdb$database ;
select (select sum(1) from rdb$database) from rdb$database ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """                COUNT
=====================
                    1


                  AVG
=====================
                    1


                  SUM
=====================
                    1

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

