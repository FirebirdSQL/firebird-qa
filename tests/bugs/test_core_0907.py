#coding:utf-8
#
# id:           bugs.core_0907
# title:        Server crash on violation of NOT NULL constraint
# decription:   
# tracker_id:   CORE-907
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_907-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table crash (a1 integer,a2 integer,a3 integer, a4 integer) ;
    commit;
    insert into crash (a1, a2, a3, a4) values ( 1, 2, 3, 4);
    insert into crash (a1, a2, a3    ) values ( 2, 3, 4   );
    insert into crash (a1, a2,     a4) values ( 2, 3,    4);
    commit;
    alter table crash add a5 computed by (a2*a3*a4);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Since 3.0 one may do like this (and NOT by updating RDB tables):
    -- ALTER TABLE <table name> ALTER <field name> [NOT] NULL
    -- ALTER DOMAIN <domain name> [NOT] NULL
    -- :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    -- 02.04.2015: since rev. 61204 (build 3.0.0.31767)syntax of altering nullability for 
    -- domains and tables has been changed: mandatory SET | DROP clause now needed, i.e.:
    -- ALTER TABLE <table name> ALTER <field name> {DROP | SET} NOT NULL
    -- ALTER DOMAIN <domain name> {DROP | SET} NOT NULL
    -- :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
    
    -- This attempt will FAIL with message:
    -- -Cannot make field A5 of table CRASH NOT NULL because there are NULLs present
    alter table crash alter a5 SET not null; 
    commit;
    
    update crash set a3=1 where a3 is null;
    update crash set a4=1 where a4 is null;
    commit;
    
    alter table crash alter a1 SET not null; 
    alter table crash alter a2 SET not null; 
    alter table crash alter a3 SET not null; 
    alter table crash alter a4 SET not null; 
    alter table crash alter a5 SET not null; 
    commit;
    update crash set a1=null, a2=null, a3=null,a4=null rows 1;
    commit;
    show table crash;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A1                              INTEGER Not Null 
    A2                              INTEGER Not Null 
    A3                              INTEGER Not Null 
    A4                              INTEGER Not Null 
    A5                              Computed by: (a2*a3*a4)
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22006
    unsuccessful metadata update
    -Cannot make field A5 of table CRASH NOT NULL because there are NULLs present
    Statement failed, SQLSTATE = 23000
    validation error for column "CRASH"."A1", value "*** null ***"
  """

@pytest.mark.version('>=3.0')
def test_core_0907_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

