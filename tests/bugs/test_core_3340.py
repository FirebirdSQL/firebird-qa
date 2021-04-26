#coding:utf-8
#
# id:           bugs.core_3340
# title:        Error in autonomous transaction with empty exception handler: can insert duplicate values into PK/UK column (leads to unrestorable backup)
# decription:   
# tracker_id:   CORE-3340
# min_versions: ['2.5.1']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """recreate table tmp(id int not null primary key using index tmp_id_pk);
commit;
set transaction no wait isolation level read committed;
set term ^;
execute block as
begin
  insert into tmp values(1);
  insert into tmp values(2);
  in autonomous transaction do begin
     insert into tmp values(1);
     when any do begin
        --exception;
     end
  end
end^
set term ;^
commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select id from tmp;
select count(*) from tmp;
commit;"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          ID
============
           1
           2


                COUNT
=====================
                    2

"""

@pytest.mark.version('>=3.0')
def test_core_3340_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

