#coding:utf-8
#
# id:           bugs.core_3057
# title:        Allow the usage of blobs in COMPUTED BY expressions
# decription:   
# tracker_id:   CORE-3057
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('BLOB_ID_.*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table test( 
        b1 blob sub_type 1 character set utf8 collate unicode_ci_ai, 
        b2 blob sub_type 1 character set utf8 collate unicode_ci_ai, 
        bconcat1 computed by ( b1 || b2 ) -- this FAILS on 2.5.4
    ); 
    commit;
    alter table test 
	     add bconcat2 computed by ( b1 || b2 || bconcat1 )
		,add brepl1_2 computed by ( replace(b1, b2, '1') )
		,add brepl2_1 computed by ( replace(b2, b1, '2') )
	;
    commit;
    --show table test;
    insert into test(b1, b2) values(
	    'ÁÉÍÓÚÝÀÈÌÒÙÂÊÎÔÛÃÑÕÄËÏÖÜŸÇŠĄĘŹŻĂŞŢ',
		'aeiouyaeiouaeiouanoaeiouycsaezzast'
	);
    
    set list on;
    set blob all;
    select 
		b1 as blob_id_b1, 
		b2 as blob_id_b2, 
		bconcat1 as blob_id_bconcat1, 
		bconcat2 as blob_id_bconcat2,
		brepl1_2 as blob_id_repl1_2,
		brepl2_1 as blob_id_repl2_1
	from test
	;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	BLOB_ID_B1                      86:0
	ÁÉÍÓÚÝÀÈÌÒÙÂÊÎÔÛÃÑÕÄËÏÖÜŸÇŠĄĘŹŻĂŞŢ
	BLOB_ID_B2                      86:1
	aeiouyaeiouaeiouanoaeiouycsaezzast
	BLOB_ID_BCONCAT1                0:12
	ÁÉÍÓÚÝÀÈÌÒÙÂÊÎÔÛÃÑÕÄËÏÖÜŸÇŠĄĘŹŻĂŞŢaeiouyaeiouaeiouanoaeiouycsaezzast
	BLOB_ID_BCONCAT2                0:f
	ÁÉÍÓÚÝÀÈÌÒÙÂÊÎÔÛÃÑÕÄËÏÖÜŸÇŠĄĘŹŻĂŞŢaeiouyaeiouaeiouanoaeiouycsaezzastÁÉÍÓÚÝÀÈÌÒÙÂÊÎÔÛÃÑÕÄËÏÖÜŸÇŠĄĘŹŻĂŞŢaeiouyaeiouaeiouanoaeiouycsaezzast
	BLOB_ID_REPL1_2                 0:8
	1
	BLOB_ID_REPL2_1                 0:5
	2
  """

@pytest.mark.version('>=3.0')
def test_core_3057_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

