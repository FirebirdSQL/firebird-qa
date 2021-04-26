#coding:utf-8
#
# id:           bugs.core_2317
# title:        select * from (select cast(.... returns null
# decription:   
# tracker_id:   CORE-2317
# min_versions: []
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """
	CREATE TABLE PROC(
	  PROC Char(10) NOT NULL,
	  TPRO Char(10) NOT NULL,
	  ACTO Varchar(200) NOT NULL,
	  CONSTRAINT PROC_PK PRIMARY KEY (PROC)
	);

	CREATE TABLE TPRO(
	  TPRO Char(10) NOT NULL,
	  CONSTRAINT TPRO_PK PRIMARY KEY (TPRO)
	);

	CREATE VIEW PROC1 (PROC, ACTO)
	AS SELECT "PROC"."PROC","PROC"."ACTO" FROM "PROC" left outer join "TPRO" on "PROC"."TPRO"="TPRO"."TPRO";

	insert into proc values ('1R1oK3qxdM', '1', '2');
	insert into tpro values ('1');
	commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
	set list on;
	-- returns NULL
	select * from (select cast("ACTO" as character(100)) as "D_COL1" from "PROC1" where "PROC"='1R1oK3qxdM') AA;
	-- returns the correct value
	select * from (select cast("ACTO" as character(100)) as "D_COL1" from "PROC" where "PROC"='1R1oK3qxdM') AA;
	select * from (select "ACTO" as "D_COL1" from "PROC1" where "PROC"='1R1oK3qxdM') AA;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	D_COL1                          2
	D_COL1                          2
	D_COL1                          2  
  """

@pytest.mark.version('>=2.5')
def test_core_2317_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

