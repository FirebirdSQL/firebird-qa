#coding:utf-8

"""
ID:          issue-1353
ISSUE:       1353
TITLE:       AV when blob is used in expression index
DESCRIPTION:
JIRA:        CORE-952
FBTEST:      bugs.core_0952
"""

import pytest
from firebird.qa import *

init_script = """create table T (
     ID integer not null,
     N1 blob sub_type 1 segment size 80,
     N2 varchar(10)
);
commit;

insert into T (ID, N1, N2) values (1, 'www', 'qwer');
commit;

alter table T add constraint PK_T primary key (ID);
create index T_IDX on T computed by (cast(substring(N1 from 1 for 100) as varchar(100)));
commit;

update T set T.N2 = 'asdf' where T.ID = 1;
commit;
"""

db = db_factory(init=init_script)

test_script = """SELECT ID,N2 FROM T;
"""

act = isql_act('db', test_script)

expected_stdout = """ID N2
============ ==========
           1 asdf

"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

