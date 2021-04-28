#coding:utf-8
#
# id:           bugs.core_2215
# title:        GROUP BY concatenation with empty string
# decription:   
# tracker_id:   CORE-2215
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE ATTRIBUTES_DICTIONARY (
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

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select ATR.name, count(*)
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

