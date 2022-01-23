#coding:utf-8

"""
ID:          issue-4638
ISSUE:       4638
TITLE:       Usage of field(s) alias in view WITH CHECK OPTION leads to incorrect compile error or incorrect internal triggers
DESCRIPTION:
JIRA:        CORE-4315
"""

import pytest
from firebird.qa import *

init_script = """
    recreate view v1 as select 1 id from rdb$database;
    commit;
    recreate table t1 (n1 integer, n2 integer);
"""

db = db_factory(init=init_script)

test_script = """
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

act = isql_act('db', test_script, substitutions=[('RDB\\$TRIGGER_BLR.*', '')])

expected_stdout = """
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
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout

