#coding:utf-8
#
# id:           bugs.core_3418
# title:        Database trigger created as INACTIVE is active
# decription:   
# tracker_id:   CORE-3418
# min_versions: ['2.1.5']
# versions:     2.1.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1.5
# resources: None

substitutions_1 = [('[ \t]+', ' ')]

init_script_1 = """
	set term ^ ;
	create or alter trigger trg$start inactive on transaction start position 0 as
	begin
		rdb$set_context('USER_SESSION', 'TRANS_ID', current_transaction);
	end
	^
	set term ; ^
	commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    select rdb$get_context('USER_SESSION', 'TRANS_ID') as ctx_var from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CTX_VAR                         <null>  
  """

@pytest.mark.version('>=2.1.5')
def test_core_3418_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

