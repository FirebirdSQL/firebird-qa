#coding:utf-8

"""
ID:          table.alter-13
TITLE:       ALTER TABLE - ALTER CONSTRAINT
DESCRIPTION:
FBTEST:      functional.table.alter.13
NOTES:
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """RECREATE TABLE test_constraints(
 id integer not null constraint pk_c primary key,
 unq integer constraint uk unique,
 nn integer constraint not_null not null,
 fk integer constraint fk references test_constraints (id),
 chk integer constraint chk check(chk=1)
);
-- Default activity of constraint is already checked in create/test_08
insert into test_constraints values(1,1,1,1,1);
commit;
-- Check deactivation of constraints
alter table test_constraints
  alter constraint uk not enforced,
  alter constraint not_null not enforced,
  alter constraint fk not enforced,
  alter constraint chk not enforced;
alter table test_constraints
  alter constraint pk_c not enforced;
commit;
-- check that none of these constraints are not enforced now
insert into test_constraints values(1,1,NULL,11,11);
rollback;
-- Check activation of constraints
alter table test_constraints
  alter constraint pk_c enforced,
  alter constraint uk enforced,
  alter constraint not_null enforced,
  alter constraint fk enforced,
  alter constraint chk enforced;
commit;
-- Check that every one has been activated
insert into test_constraints values (1,2,2,1,1); -- pk_c violation
insert into test_constraints values (3,1,3,1,1); -- uk violation
insert into test_constraints values (4,4,NULL,1,1); -- nn violation
insert into test_constraints values (5,5,5,11,1); -- fk violation
insert into test_constraints values (6,6,6,1,11); -- chk violation
"""

act = isql_act('db', test_script, substitutions=[('CHECK_[0-9]+', '')])

expected_stdout = """Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "PK_C" on table "TEST_CONSTRAINTS"
-Problematic key value is ("ID" = 1)
Statement failed, SQLSTATE = 23000
violation of PRIMARY or UNIQUE KEY constraint "UK" on table "TEST_CONSTRAINTS"
-Problematic key value is ("UNQ" = 1)
Statement failed, SQLSTATE = 23000
validation error for column "TEST_CONSTRAINTS"."NN", value "*** null ***"
Statement failed, SQLSTATE = 23000
violation of FOREIGN KEY constraint "FK" on table "TEST_CONSTRAINTS"
-Foreign key reference target does not exist
-Problematic key value is ("FK" = 11)
Statement failed, SQLSTATE = 23000
Operation violates CHECK constraint CHK on view or table TEST_CONSTRAINTS
-At trigger 'CHECK_1'
"""

@pytest.mark.version('>=6')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
