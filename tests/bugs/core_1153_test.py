#coding:utf-8

"""
ID:          issue-1574
ISSUE:       1574
TITLE:       Activating index change "STARTING" working as "LIKE" in join condition
DESCRIPTION:
JIRA:        CORE-1153
FBTEST:      bugs.core_1153
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE D (
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

db = db_factory(init=init_script)

test_script = """SET PLAN ON;

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

act = isql_act('db', test_script)

expected_stdout = """PLAN SORT (JOIN (MM NATURAL, DD NATURAL))

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

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

