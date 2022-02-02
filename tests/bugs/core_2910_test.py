#coding:utf-8

"""
ID:          issue-3294
ISSUE:       3294
TITLE:       PK index is not used for derived tables
DESCRIPTION:
JIRA:        CORE-2910
FBTEST:      bugs.core_2910
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE R$TMP (
    POSTING_ID INTEGER
);

CREATE TABLE TMP (
    POSTING_ID INTEGER NOT NULL
);

ALTER TABLE TMP ADD CONSTRAINT PK_TMP PRIMARY KEY (POSTING_ID);
commit;
"""

db = db_factory(charset='UTF8', init=init_script)

test_script = """SET PLAN ON;
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

act = isql_act('db', test_script)

expected_stdout = """
PLAN JOIN (R R$TMP NATURAL, T TMP INDEX (PK_TMP))
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

