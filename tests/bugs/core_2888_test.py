#coding:utf-8
#
# id:           bugs.core_2888
# title:        A memory corruption cause incorrect query evaluation and may crash the server
# decription:   
# tracker_id:   CORE-2888
# min_versions: ['2.1.4']
# versions:     2.1.4
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.4
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select 1 from rdb$database where 1 in (select (select current_connection from rdb$database) from rdb$database);
select 1 from rdb$database where 1 in (select (select 1 from rdb$database) from rdb$database);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Database:  localhost:C:btest2	mpugs.core_2888.fdb, User: SYSDBA
SQL> SQL>
    CONSTANT
============
           1

SQL>"""

@pytest.mark.version('>=2.1.4')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

