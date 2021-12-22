#coding:utf-8
#
# id:           functional.trigger.database.connect_03
# title:        Multiple triggers on database connect. See also CORE-745
# decription:   This tests normal operation of database CONNECT triggers when there are more of them.
# tracker_id:   
# min_versions: []
# versions:     2.1
# qmid:         functional.trigger.database.connect_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """
	create table LOG (ID integer, MSG varchar(100));
	create generator LOGID;
	set term ^;
	create trigger LOG_BI for LOG active before insert position 0
	as
	begin
	  if (new.ID is null) then
		new.ID = gen_id(LOGID,1);
	end ^

	create trigger ONCONNECT_1 on connect position 0
	as
	begin
	  insert into LOG (MSG) values ('Connect T1');
	end ^

	create trigger ONCONNECT_2 on connect position 10
	as
	begin
	  insert into LOG (MSG) values ('Connect T2');
	end ^

	set term ;^

	commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
	select * from LOG;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	ID                              1
	MSG                             Connect T1
	ID                              2
	MSG                             Connect T2  
"""

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

