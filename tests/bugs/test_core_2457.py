#coding:utf-8
#
# id:           bugs.core_2457
# title:         UNICODE_CI internal gds software consistency check
# decription:   
# tracker_id:   CORE-2457
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE ATABLE (
    AFIELD VARCHAR(50) CHARACTER SET UTF8 COLLATE UNICODE_CI);
CREATE DESCENDING INDEX ATABLE_BWD ON ATABLE (AFIELD);
COMMIT;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT FIRST 1 T.AFIELD FROM ATABLE T
  WHERE T.AFIELD < 'X'
  ORDER BY T.AFIELD DESC;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.2')
def test_core_2457_1(act_1: Action):
    act_1.execute()

