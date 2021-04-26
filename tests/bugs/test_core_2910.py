#coding:utf-8
#
# id:           bugs.core_2910
# title:        PK index is not used for derived tables
# decription:   
# tracker_id:   CORE-2910
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE R$TMP (
    POSTING_ID INTEGER
);

CREATE TABLE TMP (
    POSTING_ID INTEGER NOT NULL
);

ALTER TABLE TMP ADD CONSTRAINT PK_TMP PRIMARY KEY (POSTING_ID);
commit;
"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;
select r.POSTING_ID as r$POSTING_ID, t.POSTING_ID from (
      SELECT POSTING_ID
      FROM r$tmp
    ) r left join (
        select POSTING_ID from
          (select
            posting_id
          from tmp)
    ) t on r.POSTING_ID = t.POSTING_ID;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
PLAN JOIN (R R$TMP NATURAL, T TMP INDEX (PK_TMP))
"""

@pytest.mark.version('>=2.5.0')
def test_core_2910_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

