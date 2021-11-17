#coding:utf-8
#
# id:           bugs.core_3548
# title:        GFIX returns an error after correctly shutting down a database
# decription:   Affected only local connections
# tracker_id:   CORE-3548
# min_versions: ['2.5.5']
# versions:     2.5.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import SrvStatFlag

# version: 2.5.5
# resources: None

substitutions_1 = [('^((?!Attribute|connection).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# db_conn.close()
#  runProgram('gfix',['$(DATABASE_LOCATION)bugs.core_3548.fdb','-shut','full','-force','0','-user',user_name,'-password',user_password])
#  runProgram('gstat',['$(DATABASE_LOCATION)bugs.core_3548.fdb','-h','-user',user_name,'-password',user_password])
#  runProgram('gfix',['$(DATABASE_LOCATION)bugs.core_3548.fdb','-online','-user',user_name,'-password',user_password])
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    Attributes		force write, full shutdown
"""

@pytest.mark.version('>=2.5.5')
def test_1(act_1: Action):
    act_1.gfix(switches=['-user', act_1.db.user, '-password', act_1.db.password,
                         '-shut', 'full', '-force', '0', str(act_1.db.db_path)])
    with act_1.connect_server() as srv:
        srv.database.get_statistics(database=str(act_1.db.db_path), flags=SrvStatFlag.HDR_PAGES)
        stats = srv.readlines()
    act_1.gfix(switches=['-user', act_1.db.user, '-password', act_1.db.password,
                         '-online', str(act_1.db.db_path)])
    act_1.stdout = '\n'.join(stats)
    act_1.expected_stdout = expected_stdout_1
    assert act_1.clean_stdout == act_1.clean_expected_stdout

