#coding:utf-8

"""
ID:          isql.issue-2358
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/2358
TITLE:       ISQL showing inactive constraints
DESCRIPTION:
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """RECREATE TABLE test_constraints(
 id integer not null constraint pk_c primary key,
 unq_act_def integer constraint uk_act_def unique,
 unq_act integer constraint uk_act unique enforced,
 unq_inact integer constraint uk_inact unique not enforced,
 nn_act_def integer constraint not_null_act_def not null,
 nn_act integer constraint not_null_act not null enforced,
 nn_inact integer constraint not_null_inact not null not enforced,
 fk_act_def integer constraint fk_act_def references test_constraints (id),
 fk_act integer constraint fk_act references test_constraints (id) enforced,
 fk_inact integer constraint fk_inact references test_constraints (id) not enforced,
 check_act_def integer constraint check_act_def check(check_act_def=1),
 check_act integer constraint check_act check(check_act=1) enforced,
 check_inact integer constraint check_inact check(check_inact=1) not enforced
);
commit;
show table test_constraints;
show check test_constraints;
show index test_constraints;
"""

act = isql_act('db', test_script, substitutions=[('CHECK_[0-9]+', '')])

expected_stdout = """ID                              INTEGER Not Null
UNQ_ACT_DEF                     INTEGER Nullable
UNQ_ACT                         INTEGER Nullable
UNQ_INACT                       INTEGER Nullable
NN_ACT_DEF                      INTEGER Not Null
NN_ACT                          INTEGER Not Null
NN_INACT                        INTEGER Nullable
FK_ACT_DEF                      INTEGER Nullable
FK_ACT                          INTEGER Nullable
FK_INACT                        INTEGER Nullable
CHECK_ACT_DEF                   INTEGER Nullable
CHECK_ACT                       INTEGER Nullable
CHECK_INACT                     INTEGER Nullable
CONSTRAINT FK_ACT:
  Foreign key (FK_ACT)    References TEST_CONSTRAINTS (ID)
CONSTRAINT FK_ACT_DEF:
  Foreign key (FK_ACT_DEF)    References TEST_CONSTRAINTS (ID)
CONSTRAINT FK_INACT:
  Foreign key (FK_INACT)    References TEST_CONSTRAINTS (ID) Not enforced
CONSTRAINT PK_C:
  Primary key (ID)
CONSTRAINT UK_ACT:
  Unique key (UNQ_ACT)
CONSTRAINT UK_ACT_DEF:
  Unique key (UNQ_ACT_DEF)
CONSTRAINT UK_INACT:
  Unique key (UNQ_INACT) Not enforced
CONSTRAINT NOT_NULL_ACT_DEF:
  Not Null Column (NN_ACT_DEF)
CONSTRAINT NOT_NULL_ACT:
  Not Null Column (NN_ACT)
CONSTRAINT NOT_NULL_INACT:
  Not Null Column (NN_INACT) Not enforced
CONSTRAINT CHECK_ACT:
  check(check_act=1)
CONSTRAINT CHECK_ACT_DEF:
  check(check_act_def=1)
CONSTRAINT CHECK_INACT:
  check(check_inact=1) Not enforced
CONSTRAINT CHECK_ACT:
  check(check_act=1)
CONSTRAINT CHECK_ACT_DEF:
  check(check_act_def=1)
CONSTRAINT CHECK_INACT:
  check(check_inact=1) Not enforced
FK_ACT INDEX ON TEST_CONSTRAINTS(FK_ACT)
FK_ACT_DEF INDEX ON TEST_CONSTRAINTS(FK_ACT_DEF)
FK_INACT INDEX ON TEST_CONSTRAINTS(FK_INACT) (inactive)
PK_C UNIQUE INDEX ON TEST_CONSTRAINTS(ID)
UK_ACT UNIQUE INDEX ON TEST_CONSTRAINTS(UNQ_ACT)
UK_ACT_DEF UNIQUE INDEX ON TEST_CONSTRAINTS(UNQ_ACT_DEF)
UK_INACT UNIQUE INDEX ON TEST_CONSTRAINTS(UNQ_INACT) (inactive)
"""

#--------------------------------------------

@pytest.mark.version('>=6')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
