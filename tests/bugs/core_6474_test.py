#coding:utf-8
#
# id:           bugs.core_6474
# title:        Report replica mode through isc_database_info, MON$DATABASE and SYSTEM context
# decription:   
#                 Text verifies only ability to query replication-related info from mon$database and system context namespace.
#                 Query to isc_database_info does not perform.
#               
#                 Checked on 4.0.0.2342.
#               
#                 11.10.2021: adjusted output because variable 'REPLICA_MODE' now returns as NULL rather than empty string.
#                 Checked on 4.0.1.2628, 5.0.0.249.
#                 See commits:
#                     https://github.com/FirebirdSQL/firebird/commit/1ab406491282f06d8d8d7df260b500310b157aa1
#                     https://github.com/FirebirdSQL/firebird/commit/bedaf9d235c81f76a0ef170ed81dc1e7f47adbfa
# tracker_id:   CORE-6474
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select mon$replica_mode as mon_replica_mode from mon$database;
    select '>' || rdb$get_context('SYSTEM','REPLICA_MODE') || '<' as ctx_replica_mode from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    MON_REPLICA_MODE                0
    CTX_REPLICA_MODE                <null>
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

