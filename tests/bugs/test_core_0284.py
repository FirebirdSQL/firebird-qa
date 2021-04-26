#coding:utf-8
#
# id:           bugs.core_0284
# title:        Blob Comparison with constant
# decription:   
# tracker_id:   CORE-284
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_284

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """CREATE TABLE T1 (PK INTEGER NOT NULL, COL1 BLOB SUB_TYPE TEXT);
commit;
insert into T1 (PK,COL1) values (1,'text');
insert into T1 (PK,COL1) values (2,'');
commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select * from T1 where COL1 = '';
select * from T1 where COL1 = 'text';
commit;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          PK              COL1
============ =================
           2              80:1
==============================================================================
COL1:

==============================================================================


          PK              COL1
============ =================
           1              80:0
==============================================================================
COL1:
text
==============================================================================

"""

@pytest.mark.version('>=3.0')
def test_core_0284_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

