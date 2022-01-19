#coding:utf-8

"""
ID:          issue-1450
ISSUE:       1450
TITLE:       LIKE doesn't work for computed values (at least in a view)
DESCRIPTION:
JIRA:        CORE-1033
"""

import pytest
from firebird.qa import *

init_script = """create table TABLE_X (
  id numeric(10,0) not null,
  descr varchar(50) not null
);

commit;

create view X_VW (id, description)
as select id, x.descr || ' ('||x.id||')' from TABLE_X as x;

commit;

insert into TABLE_X values (1,'xyz');
insert into TABLE_X values (2,'xyzxyz');
insert into TABLE_X values (3,'xyz012');

commit;"""

db = db_factory(init=init_script)

test_script = """select * from X_VW ;

select * from X_VW where description like 'xyz (1)' ;

select * from X_VW where description like 'xyz (%)' ;

select * from X_VW where description like 'xyz%' ;
"""

act = isql_act('db', test_script)

expected_stdout = """
                   ID DESCRIPTION
===================== ======================================================================
                    1 xyz (1)
                    2 xyzxyz (2)
                    3 xyz012 (3)


                   ID DESCRIPTION
===================== ======================================================================
                    1 xyz (1)


                   ID DESCRIPTION
===================== ======================================================================
                    1 xyz (1)


                   ID DESCRIPTION
===================== ======================================================================
                    1 xyz (1)
                    2 xyzxyz (2)
                    3 xyz012 (3)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

