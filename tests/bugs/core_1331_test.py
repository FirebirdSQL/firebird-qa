#coding:utf-8
#
# id:           bugs.core_1331
# title:        Charset transliterations don't work with EXECUTE STATEMENT
# decription:   
# tracker_id:   CORE-1331
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_1331

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core1331-25.fbk', init=init_script_1)

test_script_1 = """
	set list on;
    select opis as direct_select from T1;
	set term ^ ;
	execute block returns ( execute_block_select varchar(100) ) as
	BEGIN
	  for select opis from t1
	  into :execute_block_select
	  do
	      SUSPEND;
	END^

	execute block returns ( execute_sttm_select varchar(100) ) as
	BEGIN
	  for execute statement 'select opis from t1'
	  into :execute_sttm_select
	  do
	      SUSPEND;
	END ^

	set term ;^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	DIRECT_SELECT                   ASCII
	DIRECT_SELECT                   милан
	EXECUTE_BLOCK_SELECT            ASCII
	EXECUTE_BLOCK_SELECT            милан
	EXECUTE_STTM_SELECT             ASCII
	EXECUTE_STTM_SELECT             милан
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

