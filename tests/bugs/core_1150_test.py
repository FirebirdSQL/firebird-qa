#coding:utf-8
#
# id:           bugs.core_1150
# title:        Error conversion error from string " " using outer join on int64 and int fields
# decription:   
# tracker_id:   CORE-1150
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1150

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE J (
    ID INTEGER NOT NULL,
    CODETABLE INTEGER,
    CODEVSPTABLE INTEGER
);


CREATE TABLE TT (
    ID BIGINT NOT NULL
);

ALTER TABLE TT ADD CONSTRAINT PK_TT PRIMARY KEY (ID);

COMMIT;

INSERT INTO TT(ID) VALUES(1);
COMMIT;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SELECT 1
  FROM TT T1 LEFT JOIN J ON J.CODETABLE = T1.ID
       LEFT JOIN TT T2 ON J.CODEVSPTABLE = T2.ID ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """CONSTANT
============
           1

"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

