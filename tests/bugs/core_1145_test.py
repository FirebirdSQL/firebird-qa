#coding:utf-8

"""
ID:          issue-1567
ISSUE:       1567
TITLE:       Server locks up while attempting to commit a deletion of an expression index
DESCRIPTION:
JIRA:        CORE-1145
FBTEST:      bugs.core_1145
"""

import pytest
from firebird.qa import *

init_script = """create table expt1 (col1 int);
create table expt2 (col2 int);
commit;

insert into expt1 values (1);
insert into expt1 values (2);

insert into expt2 values (1);
insert into expt2 values (2);
commit;

create index iexpt1 on expt1 computed (col1 + 1);
create index iexpt2 on expt2 computed (col2 + 1);
commit;
"""

db = db_factory(init=init_script)

test_script = """set plan on;
select * from expt1 where col1 + 1 = 2;
select * from expt2 where col2 + 1 = 2;
commit;

drop index iexpt2;
commit; -- lockup

select * from expt1 where col1 + 1 = 2;
select * from expt2 where col2 + 1 = 2;
commit;
"""

act = isql_act('db', test_script)

expected_stdout = """
PLAN (EXPT1 INDEX (IEXPT1))

        COL1
============
           1


PLAN (EXPT2 INDEX (IEXPT2))

        COL2
============
           1


PLAN (EXPT1 INDEX (IEXPT1))

        COL1
============
           1


PLAN (EXPT2 NATURAL)

        COL2
============
           1

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

