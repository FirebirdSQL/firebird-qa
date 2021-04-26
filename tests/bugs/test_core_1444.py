#coding:utf-8
#
# id:           bugs.core_1444
# title:        Execute statement 'select ....' into new....
# decription:   
# tracker_id:   CORE-1444
# min_versions: []
# versions:     2.0.2
# qmid:         bugs.core_1444

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.2
# resources: None

substitutions_1 = []

init_script_1 = """CREATE EXCEPTION DEXC '???';

CREATE TABLE TEST
(
  C1 char(31),
  C2 char(31)
);

commit;

SET TERM ^ ;

CREATE TRIGGER TEST_BI FOR TEST
ACTIVE BEFORE INSERT POSITION 20
AS
declare variable sql varchar(30000);
declare variable wrk_c1 char(31);
declare variable wrk_c2 char(31);
BEGIN
   /* when new.c1,new.... isn't NULL -> execute statement work ok.
      when new.c1,new.c2, is null -> execute statement has some problem */

   sql=' select first 1 RDB$CHARACTER_SET_NAME,RDB$DEFAULT_COLLATE_NAME
         from RDB$CHARACTER_SETS
         where RDB$CHARACTER_SET_NAME is not null';

   execute statement sql
   into new.c1,new.c2;

   select first 1 RDB$CHARACTER_SET_NAME,RDB$DEFAULT_COLLATE_NAME
   from RDB$CHARACTER_SETS
   where RDB$CHARACTER_SET_NAME is not null
   into :wrk_c1,:wrk_c2;

   if (wrk_c1 is not null and
       new.c1 is null) then
      exception dexc 'Is it a bug ? I think yes, it is.';
END
^
set term ; ^

commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """/* Bug */
insert into test(C1,C2) values (NULL,NULL);

/* OK */
insert into test(C1,C2) values ('A','A');

commit;

select * from test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
C1                              C2
=============================== ===============================
NONE                            NONE
NONE                            NONE

"""

@pytest.mark.version('>=2.0.2')
def test_core_1444_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

