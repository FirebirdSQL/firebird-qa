#coding:utf-8
#
# id:           bugs.core_3697
# title:        String truncation error when selecting from a VIEW with UNION inside
# decription:   
# tracker_id:   CORE-3697
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3697-ods11.fbk', init=init_script_1)

test_script_1 = """
	-- Confirmed on 2.5.1:
	-- Statement failed, SQLSTATE = 22001
	-- arithmetic exception, numeric overflow, or string truncation
	-- -string right truncation
  
	create or alter view TREE_TEST (
		ID, TEXT, PARENTID, CONDITIONS,
		STMT, RULFNAME )
	as
	select 0, 'Организации', NULL, '', ''
	 , 'KODORG'
	 from rdb$database
	union
	select uidorg
	 , nameorg
	 , '0'
	 , ' G.UIDORG = ' || '''' || uidorg || ''''
	 , ''
	 , 'KODORG'
	 from org_delivery
	;
	commit;

	set list on;
	select id, text, parentid, conditions, stmt, rulfname
	from tree_test;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	ID                              0
	TEXT                            Организации
	PARENTID                        <null>
	CONDITIONS                      
	STMT                            
	RULFNAME                        KODORG                                                                                          

	ID                              7707083893     380000460
	TEXT                            АНГАРСКОЕ ОТДЕЛЕНИЕ № 7690
	PARENTID                        0               
	CONDITIONS                       G.UIDORG = '7707083893     380000460'
	STMT                            
	RULFNAME                        KODORG                                                                                          

	ID                              7724261610     380000326
	TEXT                            ПОЧТАМТ
	PARENTID                        0               
	CONDITIONS                       G.UIDORG = '7724261610     380000326'
	STMT                            
	RULFNAME                        KODORG       
"""

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

