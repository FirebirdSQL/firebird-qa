#coding:utf-8
#
# id:           bugs.core_2426
# title:        Alter table not respecting collation
# decription:   
# tracker_id:   CORE-2426
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """-- create domain A_DOMAIN VARCHAR(14) CHARacter SET WIN1252 COLLATE WINPT_BR;
create domain A_DOMAIN VARCHAR(14) CHARacter SET WIN1252;
create domain B_DOMAIN VARCHAR(14) CHARacter SET ISO8859_1 COLLATE PT_BR;

create table t (FIELD_A VARCHAR(14) CHARacter SET WIN1252 not null COLLATE WIN1252);
alter table t alter field_a type b_domain;
alter table t add primary key (FIELD_A);

create table t2 (FK B_DOMAIN REFERENCES t(FIELD_A));
show table t; -- colattion changes to de_de
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """FIELD_A                         (B_DOMAIN) VARCHAR(14) CHARACTER SET ISO8859_1 Not Null
                                 COLLATE PT_BR
CONSTRAINT INTEG_2:
  Primary key (FIELD_A)
"""

@pytest.mark.version('>=2.5')
def test_core_2426_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

