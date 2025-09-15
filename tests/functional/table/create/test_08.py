#coding:utf-8

"""
ID:          table.create-08
TITLE:       CREATE TABLE - enforced and not enforced constraints
DESCRIPTION:
FBTEST:      functional.table.create.08
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
-- check that not enforced constraints are not enforced. These inserts must pass
insert into test_constraints values (1,2,2,2,3,3,NULL,NULL,NULL,NULL,1,1,2);
insert into test_constraints values (2,22,22,2,3,3,NULL,1,1,11,1,1,2);
-- check that enforced constraints are enforced. These inserts must fail
insert into test_constraints values (1,23,23,2,3,3,3,1,1,1,1,1,1); -- pk_c violation
insert into test_constraints values (3,2,23,23,3,3,3,1,1,1,1,1,1); -- uk_act_def violation
insert into test_constraints values (4,24,2,24,3,3,3,1,1,1,1,1,1); -- uk_act violation
insert into test_constraints values (5,25,25,25,NULL,3,3,1,1,1,1,1,1); -- not_null_act_def violation
insert into test_constraints values (6,26,26,26,3,NULL,3,1,1,1,1,1,1); -- not_null_act violation
insert into test_constraints values (7,27,27,27,3,3,3,37,1,1,1,1,1); -- fk_act_def violation
insert into test_constraints values (8,28,28,28,3,3,3,1,38,1,1,1,1); -- fk_act violation
insert into test_constraints values (9,29,29,29,3,3,3,1,1,1,49,1,1); -- check_act_def violation
insert into test_constraints values (10,29,29,29,3,3,3,1,1,1,1,4,1); -- check_act violation
commit;
-- Separate check for PK
RECREATE TABLE test_constraints_pk(
 id integer not null constraint pk_c_enf primary key enforced);
insert into test_constraints_pk values(1);
insert into test_constraints_pk values(1);
rollback;
RECREATE TABLE test_constraints_pk(
 id integer not null constraint pk_c_not_enf primary key not enforced);
insert into test_constraints_pk values(1);
insert into test_constraints_pk values(1);
"""

act = isql_act('db', test_script, substitutions=[('CHECK_[0-9]+', '')])

expected_stderr = """Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "PK_C" on table "TEST_CONSTRAINTS"
-Problematic key value is ("ID" = 1)
Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "UK_ACT_DEF" on table "TEST_CONSTRAINTS"
-Problematic key value is ("UNQ_ACT_DEF" = 2)
Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "UK_ACT" on table "TEST_CONSTRAINTS"
-Problematic key value is ("UNQ_ACT" = 2)
Statement failed, SQLSTATE = 23000
validation error for column "TEST_CONSTRAINTS"."NN_ACT_DEF", value "*** null ***"
Statement failed, SQLSTATE = 23000
validation error for column "TEST_CONSTRAINTS"."NN_ACT", value "*** null ***"
Statement failed, SQLSTATE = 23000
violation of FOREIGN KEY constraint "FK_ACT_DEF" on table "TEST_CONSTRAINTS"
-Foreign key reference target does not exist
-Problematic key value is ("FK_ACT_DEF" = 37)
Statement failed, SQLSTATE = 23000
violation of FOREIGN KEY constraint "FK_ACT" on table "TEST_CONSTRAINTS"
-Foreign key reference target does not exist
-Problematic key value is ("FK_ACT" = 38)
Statement failed, SQLSTATE = 23000
Operation violates CHECK constraint CHECK_ACT_DEF on view or table TEST_CONSTRAINTS
-At trigger 'CHECK_41'
Statement failed, SQLSTATE = 23000
Operation violates CHECK constraint CHECK_ACT on view or table TEST_CONSTRAINTS
-At trigger 'CHECK_43'
Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "PK_C_ENF" on table "TEST_CONSTRAINTS_PK"
-Problematic key value is ("ID" = 1)
"""

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.execute()
    assert act.clean_stderr == act.clean_expected_stderr
