#coding:utf-8

"""
ID:          issue-2643
ISSUE:       2643
TITLE:       GROUP BY concatenation with empty string
DESCRIPTION:
JIRA:        CORE-2215
"""

import pytest
from firebird.qa import *

init_script = """CREATE TABLE ATTRIBUTES_DICTIONARY (
    ID INTEGER NOT NULL,
    NAME VARCHAR(25)
);

insert into ATTRIBUTES_DICTIONARY (ID, NAME)
 values (1,'ATTR1');
insert into ATTRIBUTES_DICTIONARY (ID, NAME)
 values (2,'ATTR1');
insert into ATTRIBUTES_DICTIONARY (ID, NAME)
 values (3,'ATTR2');

commit;
"""

db = db_factory(init=init_script)

test_script = """select ATR.name, count(*)
  from ATTRIBUTES_DICTIONARY ATR
  group by 1 order by 2 desc ;

select ATR.name||'TEXT', count(*)
  from ATTRIBUTES_DICTIONARY ATR
  group by 1 order by 2 desc ;

select ATR.name||'', count(*)
  from ATTRIBUTES_DICTIONARY ATR
  group by 1 order by 2 desc ;

select ATR.name||'', count(*)
  from ATTRIBUTES_DICTIONARY ATR
  group by ATR.name||'' order by count(*) desc ;
"""

act = isql_act('db', test_script)

expected_stdout = """
NAME                                      COUNT
========================= =====================
ATTR1                                         2
ATTR2                                         1


CONCATENATION                                 COUNT
============================= =====================
ATTR1TEXT                                         2
ATTR2TEXT                                         1


CONCATENATION                             COUNT
========================= =====================
ATTR1                                         2
ATTR2                                         1


CONCATENATION                             COUNT
========================= =====================
ATTR1                                         2
ATTR2                                         1

"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

