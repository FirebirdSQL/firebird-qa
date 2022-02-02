#coding:utf-8

"""
ID:          issue-2434
ISSUE:       2434
TITLE:       Broken foreign key handling for multi-segmented index using multi-level collations
DESCRIPTION:
JIRA:        CORE-1997
FBTEST:      bugs.core_1997
"""

import pytest
from firebird.qa import *

init_script = """create table pk (
    c1 varchar (5) character set utf8 collate unicode_ci,
    c2 varchar (5) character set utf8 collate unicode_ci,
    primary key (c1, c2)
);
commit;
create table fk (
    c1 varchar (5) character set utf8 collate unicode_ci,
    c2 varchar (5) character set utf8 collate unicode_ci,
    foreign key (c1, c2) references pk
);
commit;
insert into pk values ('a', 'b');
insert into fk values ('A', 'b');
commit;
"""

db = db_factory(init=init_script)

test_script = """delete from pk; -- should not be allowed
"""

act = isql_act('db', test_script)

expected_stderr = """Statement failed, SQLSTATE = 23000
violation of FOREIGN KEY constraint "INTEG_2" on table "FK"
-Foreign key references are present for the record
-Problematic key value is ("C1" = 'a', "C2" = 'b')
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr

