#coding:utf-8
#
# id:           bugs.core_4733
# title:        Command "Alter table <T> alter TYPE <C> <DOMAIN_WITH_NOT_NULL" does not verifies data in column <C> and makes incorrect assignments in <C> to ZERO / JULIAN_DATE / ASCII(0) for types INT, TIMESTAMP and VARCHAR
# decription:   
# tracker_id:   CORE-4733
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Tests that manipulates with NULL fields/domains and check results:
    -- CORE-1518 Adding a non-null restricted column to a populated table renders the table inconsistent
    -- CORE-4453 (Regression: NOT NULL constraint, declared in domain, does not work)
    -- CORE-4725 (Inconsistencies with ALTER DOMAIN and ALTER TABLE with DROP NOT NULL and PRIMARY KEYs)
    -- CORE-4733 (Command "Alter table <T> alter TYPE <C> <DOMAIN_WITH_NOT_NULL" does not verifies data in column <C> and makes incorrect assignments in <C> to ZERO / JULIAN_DATE / ASCII(0) for types INT, TIMESTAMP and VARCHAR)

    create domain dm_nn_int int NOT null;
    create domain dm_nn_dts timestamp NOT null;
    create domain dm_nn_utf varchar(10) character set utf8 NOT null;
    create domain dm_nn_boo boolean NOT null;

    set list on;

    create table test(num int, dts timestamp, str varchar(10) character set utf8, boo boolean);
    commit;

    insert into test values(null, null, null, null);
    commit;

    alter table test 
        alter num type dm_nn_int
        ,alter dts type dm_nn_dts 
        ,alter str type dm_nn_utf
        ,alter boo type dm_nn_boo
    ;
    commit;

    show table test;

    delete from test returning num, dts, str, boo;
    commit;

    alter table test 
        alter num type dm_nn_int
        ,alter dts type dm_nn_dts 
        ,alter str type dm_nn_utf
        ,alter boo type dm_nn_boo
    ;

    commit;
    insert into test values(null, null, null, null);
    commit;
    show table test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    NUM                             INTEGER Nullable 
    DTS                             TIMESTAMP Nullable 
    STR                             VARCHAR(10) CHARACTER SET UTF8 Nullable 
    BOO                             BOOLEAN Nullable 

    NUM                             <null>
    DTS                             <null>
    STR                             <null>
    BOO                             <null>


    NUM                             (DM_NN_INT) INTEGER Not Null 
    DTS                             (DM_NN_DTS) TIMESTAMP Not Null 
    STR                             (DM_NN_UTF) VARCHAR(10) CHARACTER SET UTF8 Not Null 
    BOO                             (DM_NN_BOO) BOOLEAN Not Null 
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22006
    unsuccessful metadata update
    -Cannot make field NUM of table TEST NOT NULL because there are NULLs present
    -Cannot make field DTS of table TEST NOT NULL because there are NULLs present
    -Cannot make field STR of table TEST NOT NULL because there are NULLs present
    -Cannot make field BOO of table TEST NOT NULL because there are NULLs present
    Statement failed, SQLSTATE = 23000
    validation error for column "TEST"."NUM", value "*** null ***"
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

