#coding:utf-8
#
# id:           bugs.core_1971
# title:        Set the fixed and documented check order for WHERE clause and other conditional sentences
# decription:   
# tracker_id:   CORE-1971
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """
    create table t_links (
      link_type integer,
      right_id integer,
      prop_value varchar(1024)
    );

    insert into t_links (link_type,right_id,prop_value) values(2,161,'2001');
    insert into t_links (link_type,right_id,prop_value) values(2,161,'2002');
    insert into t_links (link_type,right_id,prop_value) values(2,161,'2003');
    insert into t_links (link_type,right_id,prop_value) values(10,161,'any string');
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select * from t_links
    where (right_id=161 and link_type=2) and cast(prop_value as integer)<>2001;

    select * from t_links
    where cast(prop_value as integer)<>2001 and (right_id=161 and link_type=2);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	LINK_TYPE                       2
	RIGHT_ID                        161
	PROP_VALUE                      2002
	
	LINK_TYPE                       2
	RIGHT_ID                        161
	PROP_VALUE                      2003
	
	LINK_TYPE                       2
	RIGHT_ID                        161
	PROP_VALUE                      2002
	
	LINK_TYPE                       2
	RIGHT_ID                        161
	PROP_VALUE                      2003  
  """
expected_stderr_1 = """
    Statement failed, SQLSTATE = 22018
    conversion error from string "any string"
  """

@pytest.mark.version('>=2.5.0')
def test_core_1971_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr
    assert act_1.clean_expected_stdout == act_1.clean_stdout

