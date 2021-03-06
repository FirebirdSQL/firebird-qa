#coding:utf-8
#
# id:           bugs.core_4315
# title:        Usage of field(s) alias in view WITH CHECK OPTION leads to incorrect compile error or incorrect internal triggers
# decription:   
# tracker_id:   CORE-4315
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('RDB\\$TRIGGER_BLR.*', '')]

init_script_1 = """
    recreate view v1 as select 1 id from rdb$database;
    commit;
    recreate table t1 (n1 integer, n2 integer);
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Compilation error in LI-T3.0.0.30830 (13-jan-2014): "Column unknown":
    recreate view v1 as select t1.n1 from t1 t1 where t1.n1 < t1.n2 with check option;
    recreate view v1 as select t1.n1 from t1 where t1.n1 < t1.n2 with check option;
    recreate view v1 as select x.n1 from t1 x where x.n1 < x.n2 with check option;
    
    -- Compiled without errors but generates incorrect internal triggers
    recreate view v1 as select n1 a from t1 where n1 < n2 with check option;
    commit;
    
    set blob all; 
    set list on;
    select rdb$trigger_blr
    from rdb$triggers 
    where upper(trim(rdb$relation_name))=upper('v1')
    order by rdb$trigger_name;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
RDB$TRIGGER_BLR                 c:2d2
        	blr_version5,
        	blr_begin,
        	   blr_for,
        	      blr_rse, 1,
        	         blr_relation, 2, 'T','1', 2,
        	         blr_boolean,
        	            blr_and,
        	               blr_lss,
        	                  blr_field, 2, 2, 'N','1',
        	                  blr_field, 2, 2, 'N','2',
        	               blr_equiv,
        	                  blr_field, 0, 1, 'A',
        	                  blr_field, 2, 2, 'N','1',
        	         blr_end,
        	      blr_if,
        	         blr_lss,
        	            blr_field, 1, 1, 'A',
        	            blr_field, 2, 2, 'N','2',
        	         blr_begin,
        	            blr_end,
        	         blr_abort, blr_gds_code, 16, 'c','h','e','c','k','_','c','o','n','s','t','r','a','i','n','t',
        	   blr_end,
        	blr_eoc


RDB$TRIGGER_BLR                 c:2d3
        	blr_version5,
        	blr_begin,
        	   blr_if,
        	      blr_lss,
        	         blr_field, 1, 1, 'A',
        	         blr_null,
        	      blr_begin,
        	         blr_end,
        	      blr_abort, blr_gds_code, 16, 'c','h','e','c','k','_','c','o','n','s','t','r','a','i','n','t',
        	   blr_end,
        	blr_eoc
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

