#coding:utf-8
#
# id:           bugs.core_2303
# title:         Include PLAN in mon$statements
# decription:   
#                   21-05-2017:
#                   fb30Cs, build 3.0.3.32725: OK, 1.406ss.
#                   fb30SC, build 3.0.3.32725: OK, 0.828ss.
#                   FB30SS, build 3.0.3.32725: OK, 0.829ss.
#                   FB40CS, build 4.0.0.645: OK, 1.718ss.
#                   FB40SC, build 4.0.0.645: OK, 0.968ss.
#                   FB40SS, build 4.0.0.645: OK, 0.969ss.
#                
# tracker_id:   CORE-2303
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('MON_EXPLAINED_BLOB_ID .*', '')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set blob all;
    set list on;
    commit;
    select
        (select sign(count(*)) from rdb$relations r)
       ,s.mon$explained_plan as mon_explained_blob_id
    from mon$statements s
    where 
    s.mon$transaction_id = current_transaction
    and s.mon$sql_text containing 'from mon$statements' -- prevent from RDB$AUTH record, 4.0 Classic
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    SIGN                            1
    
    Select Expression
        -> Singularity Check
            -> Aggregate
                -> Table "RDB$RELATIONS" as "R" Full Scan
    Select Expression
        -> Filter
            -> Table "MON$STATEMENTS" as "S" Full Scan
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

