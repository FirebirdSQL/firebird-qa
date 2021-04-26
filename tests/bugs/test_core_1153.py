#coding:utf-8
#
# id:           bugs.core_1153
# title:        Activating index change "STARTING" working as "LIKE" in join condition
# decription:   
# tracker_id:   CORE-1153
# min_versions: []
# versions:     2.0.2
# qmid:         bugs.core_1153

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.2
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE D (
    ID  VARCHAR(40)
);


CREATE TABLE M (
    ID  VARCHAR(40)
);


INSERT INTO D (ID) VALUES ('AAA');
INSERT INTO D (ID) VALUES ('aaa');
INSERT INTO D (ID) VALUES ('Aaa Aaa');
INSERT INTO D (ID) VALUES ('BBB');
INSERT INTO D (ID) VALUES ('BBB');
INSERT INTO D (ID) VALUES ('CCC');

COMMIT WORK;

INSERT INTO M (ID) VALUES ('AAA Aaa');
INSERT INTO M (ID) VALUES ('AAA Bbb');
INSERT INTO M (ID) VALUES ('DDD Ddd');
INSERT INTO M (ID) VALUES ('Bbb Aaa');
INSERT INTO M (ID) VALUES ('Bbb Bbb');

COMMIT WORK;

CREATE INDEX D_IDX1 ON D COMPUTED BY (upper(id));
CREATE INDEX M_IDX1 ON M COMPUTED BY (UPPER(ID));

COMMIT WORK;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """SET PLAN ON;

ALTER INDEX D_IDX1 INACTIVE;

select distinct mm.ID as MID, dd.ID as DID
from m mm
left outer join d dd
  on upper(mm.id) starting upper(dd.id)
order by mm.id ;

ALTER INDEX D_IDX1 ACTIVE;

select distinct mm.ID as MID, dd.ID as DID
from m mm
left outer join d dd
  on upper(mm.id) starting upper(dd.id)
order by mm.id ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """PLAN SORT (JOIN (MM NATURAL, DD NATURAL))

MID                                      DID
======================================== ========================================
AAA Aaa                                  AAA
AAA Aaa                                  Aaa Aaa
AAA Aaa                                  aaa
AAA Bbb                                  AAA
AAA Bbb                                  aaa
Bbb Aaa                                  BBB
Bbb Bbb                                  BBB
DDD Ddd                                  <null>

PLAN SORT (JOIN (MM NATURAL, DD NATURAL))

MID                                      DID
======================================== ========================================
AAA Aaa                                  AAA
AAA Aaa                                  Aaa Aaa
AAA Aaa                                  aaa
AAA Bbb                                  AAA
AAA Bbb                                  aaa
Bbb Aaa                                  BBB
Bbb Bbb                                  BBB
DDD Ddd                                  <null>

"""

@pytest.mark.version('>=2.0.2')
def test_core_1153_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

