#coding:utf-8
#
# id:           bugs.core_0116
# title:        CREATE TABLE - no blob for external
# decription:   CREATE TABLE - blob not allow for external tables
#               
#               Dependencies:
#               CREATE DATABASE
#               CREATE TABLE
# tracker_id:   CORE-116
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_116-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Untill build 3.0.0.31721 STDERR was:
    -- -Data type BLOB is not supported ... field '<Missing arg #3 - possibly status vector overflow>'
    -- Since WI-T3.0.0.31733 STDERR became normal - contains name of field. 
    -- See correction in 'expected_stderr' secsion (23.03.2015).
    create table ext_log external file '$(DATABASE_LOCATION)z.dat' (F1 INT, F2 BLOB SUB_TYPE TEXT);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY004
    unsuccessful metadata update
    -CREATE TABLE EXT_LOG failed
    -SQL error code = -607
    -Invalid command
    -Data type BLOB is not supported for EXTERNAL TABLES. Relation 'EXT_LOG', field 'F2'
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

