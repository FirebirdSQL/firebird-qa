#coding:utf-8
#
# id:           bugs.core_2300
# title:        Unexpected error "arithmetic exception, numeric overflow, or string truncation" while evaluating SUBSTRING the second time
# decription:   
# tracker_id:   CORE-2300
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """set term ^ ;
create procedure p
  returns ( res varchar(10) )
as begin
  res = null;
  suspend;
  res = '0123456789';
  suspend;
end ^
set term ; ^
commit;"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select substring(res from 1 for 5) from p order by 1; -- success
select substring(res from 1 for 5) from p order by 1; -- error
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
SUBSTRING
=========
<null>
01234


SUBSTRING
=========
<null>
01234

"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

