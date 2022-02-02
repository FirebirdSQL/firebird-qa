#coding:utf-8

"""
ID:          issue-2842
ISSUE:       2842
TITLE:       Alter table not respecting collation
DESCRIPTION:
JIRA:        CORE-2426
FBTEST:      bugs.core_2426
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """-- create domain A_DOMAIN VARCHAR(14) CHARacter SET WIN1252 COLLATE WINPT_BR;
create domain A_DOMAIN VARCHAR(14) CHARacter SET WIN1252;
create domain B_DOMAIN VARCHAR(14) CHARacter SET ISO8859_1 COLLATE PT_BR;

create table t (FIELD_A VARCHAR(14) CHARacter SET WIN1252 not null COLLATE WIN1252);
alter table t alter field_a type b_domain;
alter table t add primary key (FIELD_A);

create table t2 (FK B_DOMAIN REFERENCES t(FIELD_A));
show table t; -- colattion changes to de_de
"""

act = isql_act('db', test_script)

expected_stdout = """FIELD_A                         (B_DOMAIN) VARCHAR(14) CHARACTER SET ISO8859_1 Not Null
                                 COLLATE PT_BR
CONSTRAINT INTEG_2:
  Primary key (FIELD_A)
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

