#coding:utf-8
#
# id:           bugs.core_0888
# title:        DDL - object in use
# decription:   
# tracker_id:   CORE-888
# min_versions: []
# versions:     2.0.1
# qmid:         bugs.core_888

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET TERM ^ ;
CREATE PROCEDURE TestProc
AS
BEGIN
   EXIT;
END ^
SET TERM ; ^

EXECUTE PROCEDURE TestProc;

DROP PROCEDURE TestProc;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.0.1')
def test_1(act_1: Action):
    act_1.execute()

