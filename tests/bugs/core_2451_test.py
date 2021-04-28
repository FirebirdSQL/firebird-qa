#coding:utf-8
#
# id:           bugs.core_2451
# title:        Query SELECT ... WHERE ... IN (SELECT DISTINCT ... ) returns a wrong result set.
# decription:   
# tracker_id:   CORE-2451
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TBL_TEST (FLD_VALUE INTEGER);
INSERT INTO TBL_TEST VALUES (1);
INSERT INTO TBL_TEST VALUES (2);
INSERT INTO TBL_TEST VALUES (3);
COMMIT;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT * FROM TBL_TEST WHERE FLD_VALUE IN (SELECT DISTINCT FLD_VALUE FROM TBL_TEST WHERE FLD_VALUE NOT IN (SELECT DISTINCT FLD_VALUE FROM TBL_TEST));
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.execute()

