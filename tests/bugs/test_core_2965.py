#coding:utf-8
#
# id:           bugs.core_2965
# title:        Incorrect ROW_COUNT value after SINGULAR condition
# decription:   
# tracker_id:   CORE-2965
# min_versions: ['2.5.0']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """set term !!;
execute block
returns(rcount integer)
as
declare tmpint integer;
begin
   select rdb$relation_id from rdb$database into tmpint;
   if (SINGULAR(select rdb$relation_id from rdb$database where rdb$relation_id is null)) then begin end
   rcount = row_count;
   suspend;
end!!
execute block
returns(rcount integer)
as
declare tmpint integer;
begin
   select rdb$relation_id from rdb$database into tmpint;
   if (SINGULAR(select * from rdb$relation_fields)) then begin end
   rcount = row_count;
   suspend;
end!!"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
      RCOUNT
============
           1


      RCOUNT
============
           1

"""

@pytest.mark.version('>=2.5.0')
def test_core_2965_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

