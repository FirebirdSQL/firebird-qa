#coding:utf-8
#
# id:           bugs.core_4415
# title:        Useless extraction of generic DDL trigger
# decription:   
# tracker_id:   CORE-4415
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('\\+.*', ''), ('\\=.*', ''), ('Trigger text.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    create or alter trigger tr before any ddl statement as begin end; 
    show trigger tr; 
    -- Confirmed excessive output in WI-T3.0.0.30809 Firebird 3.0 Alpha 2. Was:
    -- TR, Sequence: 0, Type: BEFORE CREATE TABLE OR ALTER TABLE OR DROP TABLE OR ... OR <unknown>, Active // length = 967 characters.
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TR, Sequence: 0, Type: BEFORE ANY DDL STATEMENT, Active
    as begin end
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

