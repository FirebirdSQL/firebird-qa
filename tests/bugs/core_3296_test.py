#coding:utf-8
#
# id:           bugs.core_3296
# title:        Error "context already in use" for the simple case function with a sub-select operand
# decription:   
# tracker_id:   CORE-3296
# min_versions: ['2.1.5']
# versions:     2.1.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.5
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE VAT_ZAK
(
  ID Integer NOT NULL,
  SYS_NR Integer,
  CONSTRAINT PK_VAT_ZAK__ID PRIMARY KEY (ID)
);

CREATE TABLE ELEMENTY
(
   ID Integer NOT NULL,
  ID_VAT_SPRZ Integer,
CONSTRAINT PK_ELEMENTY__ID PRIMARY KEY (ID)
);
COMMIT;"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """UPDATE
ELEMENTY E
SET
E.ID_VAT_SPRZ=
CASE
WHEN (SELECT V.SYS_NR FROM VAT_ZAK V WHERE V.ID=E.ID_VAT_SPRZ) = 1 THEN (SELECT V.ID FROM VAT_ZAK V WHERE V.SYS_NR=7)
WHEN (SELECT V.SYS_NR FROM VAT_ZAK V WHERE V.ID=E.ID_VAT_SPRZ) = 2 THEN (SELECT V.ID FROM VAT_ZAK V WHERE V.SYS_NR=8)
WHEN (SELECT V.SYS_NR FROM VAT_ZAK V WHERE V.ID=E.ID_VAT_SPRZ) = 3 THEN (SELECT V.ID FROM VAT_ZAK V WHERE V.SYS_NR=9)
ELSE E.ID_VAT_SPRZ END;
COMMIT;
UPDATE
ELEMENTY E
SET
E.ID_VAT_SPRZ=
CASE
(SELECT V.SYS_NR FROM VAT_ZAK V WHERE V.ID=E.ID_VAT_SPRZ)
WHEN 1 THEN (SELECT V.ID FROM VAT_ZAK V WHERE V.SYS_NR=7)
WHEN 2 THEN (SELECT V.ID FROM VAT_ZAK V WHERE V.SYS_NR=8)
WHEN 3 THEN (SELECT V.ID FROM VAT_ZAK V WHERE V.SYS_NR=9)
ELSE E.ID_VAT_SPRZ END;
COMMIT;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1.5')
def test_1(act_1: Action):
    act_1.execute()

