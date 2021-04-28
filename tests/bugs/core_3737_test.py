#coding:utf-8
#
# id:           bugs.core_3737
# title:        EXECUTE BLOCK parameters definitions are not respected and may cause wrong behavior related to character sets
# decription:   
# tracker_id:   CORE-3737
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
	set list on;
	set term ^;
	execute block returns(len_1252 int, len_utf8 int) as
		declare s varchar(16) character set utf8 = 'ÃÂÁÀÄÅÇØßÐÑÞÆŠŒŽ'; -- http://en.wikipedia.org/wiki/Windows-1252
	begin
		execute statement (
			'execute block (c varchar(16) character set win1252 = ?) returns (n int) as '
			|| 'begin '
			|| '  n = octet_length(c); '
			|| '  suspend; '
			|| 'end') (s)
		into len_1252;

		execute statement (
			'execute block (c varchar(16) character set utf8 = ?) returns (n int) as '
			|| 'begin '
			|| '  n = octet_length(c); '
			|| '  suspend; '
			|| 'end') (s)
		into len_utf8;
		suspend;
		
	end
	^
	set term ;^
	commit;  
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	LEN_1252                        16
	LEN_UTF8                        32  
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

