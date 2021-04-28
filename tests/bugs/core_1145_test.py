#coding:utf-8
#
# id:           bugs.core_1145
# title:        Server locks up while attempting to commit a deletion of an expression index
# decription:   This test may lock up the server.
# tracker_id:   CORE-1145
# min_versions: []
# versions:     2.0.2
# qmid:         bugs.core_1145

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.2
# resources: None

substitutions_1 = []

init_script_1 = """create table expt1 (col1 int);
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

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """set plan on;
select * from expt1 where col1 + 1 = 2;
select * from expt2 where col2 + 1 = 2;
commit;

drop index iexpt2;
commit; -- lockup

select * from expt1 where col1 + 1 = 2;
select * from expt2 where col2 + 1 = 2;
commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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

@pytest.mark.version('>=2.0.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

