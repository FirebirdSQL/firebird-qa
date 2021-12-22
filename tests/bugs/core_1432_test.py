#coding:utf-8
#
# id:           bugs.core_1432
# title:        Collation not propagated between record formats
# decription:   
# tracker_id:   CORE-1432
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE DOMAIN D_1250 VARCHAR(10) CHARACTER SET WIN1250 COLLATE WIN1250;
CREATE DOMAIN D_CZ VARCHAR(10) CHARACTER SET WIN1250 COLLATE WIN_CZ;

CREATE TABLE T (I INTEGER, A D_1250);
INSERT INTO T VALUES(10, 'a');
COMMIT;
"""

db_1 = db_factory(page_size=4096, charset='WIN1250', sql_dialect=3, init=init_script_1)

test_script_1 = """SET COUNT ON;

SELECT * FROM T WHERE A='A';

ALTER TABLE T ALTER A TYPE D_CZ;
commit;

SELECT * FROM T WHERE A='A';
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """Records affected: 0

           I A
============ ==========
          10 a

Records affected: 1
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

