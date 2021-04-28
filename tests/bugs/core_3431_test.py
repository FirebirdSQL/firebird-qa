#coding:utf-8
#
# id:           bugs.core_3431
# title:        ISQL pads UTF-8 data incorrectly
# decription:   
# tracker_id:   CORE-3431
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
	set term ^;
	create or alter procedure p1 returns (
	  c1 char(5) character set utf8,
	  c2 char(10) character set utf8,
	  vc1 varchar(5) character set utf8,
	  vc2 varchar(10) character set utf8
	)
	as
	begin
	  vc1 = '12345';
	  c1 = vc1;
	  c2 = vc1;
	  vc2 = vc1;
	  suspend;

	  vc1 = 'áé';
	  c1 = vc1;
	  c2 = vc1;
	  vc2 = vc1;
	  suspend;

	  vc1 = '123';
	  c1 = vc1;
	  c2 = vc1;
	  vc2 = vc1;
	  suspend;

	  vc1 = '12345';
	  c1 = vc1;
	  c2 = vc1;
	  vc2 = vc1;
	  suspend;

	  vc1 = '1234';
	  c1 = vc1;
	  c2 = vc1;
	  vc2 = vc1;
	  suspend;

	  vc1 = 'áéíóú';
	  c1 = vc1;
	  c2 = vc1;
	  vc2 = vc1;
	  suspend;
	end
	^
	set term ;^
	commit;

	-- Padding in WI-T3.0.0.31767 looks OK: checked output on NotePad++ 6.6.9
	select * from p1;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	C1     C2         VC1    VC2
	====== ========== ====== ==========
	12345  12345      12345  12345
	áé     áé         áé     áé
	123    123        123    123
	12345  12345      12345  12345
	1234   1234       1234   1234
	áéíóú  áéíóú      áéíóú  áéíóú
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

