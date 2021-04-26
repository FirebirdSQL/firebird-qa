#coding:utf-8
#
# id:           bugs.core_1172
# title:        Symbols ignored for ES_ES_CI_AI collation
# decription:   
# tracker_id:   CORE-1172
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1172

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE TABLE_A (
    FIELD_A VARCHAR(10) CHARACTER SET iso8859_1 COLLATE ES_ES_CI_AI
);

ALTER TABLE TABLE_A ADD CONSTRAINT UNQ1_TABLE_A UNIQUE (FIELD_A);

INSERT INTO TABLE_A (FIELD_A) VALUES ('A');

commit;

create collation es_es_ci_ai2 for iso8859_1 from es_es_ci_ai 'SPECIALS-FIRST=1';

CREATE TABLE TABLE_B (
    FIELD_A VARCHAR(10) CHARACTER SET iso8859_1 COLLATE ES_ES_CI_AI2
);

ALTER TABLE TABLE_B ADD CONSTRAINT UNQ1_TABLE_B UNIQUE (FIELD_A);

INSERT INTO TABLE_B (FIELD_A) VALUES ('A');

commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """INSERT INTO TABLE_A (FIELD_A) VALUES ('A.');
INSERT INTO TABLE_A (FIELD_A) VALUES ('A-');
INSERT INTO TABLE_A (FIELD_A) VALUES ('-A');
INSERT INTO TABLE_A (FIELD_A) VALUES ('(A)');
INSERT INTO TABLE_A (FIELD_A) VALUES ('(A)a');
INSERT INTO TABLE_A (FIELD_A) VALUES ('Aa');

INSERT INTO TABLE_B (FIELD_A) VALUES ('A.');
INSERT INTO TABLE_B (FIELD_A) VALUES ('A-');
INSERT INTO TABLE_B (FIELD_A) VALUES ('-A');
INSERT INTO TABLE_B (FIELD_A) VALUES ('(A)');
INSERT INTO TABLE_B (FIELD_A) VALUES ('(A)a');
INSERT INTO TABLE_B (FIELD_A) VALUES ('Aa');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.1')
def test_core_1172_1(act_1: Action):
    act_1.execute()

