#coding:utf-8
#
# id:           bugs.core_1784
# title:        Error with EXECUTE PROCEDURE inside EXECUTE STATEMENT
# decription:   
# tracker_id:   CORE-1784
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """set term ^ ;
create procedure p1 returns (n1 integer, n2 integer)
as
begin
    n1 = 111;
    n2 = 222;
end ^

set term ; ^

"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """set term ^ ;

execute block returns (n1 integer, n2 integer)
as
begin
  execute statement
    'execute procedure p1' into n1, n2;
  suspend;
end^

set term ; ^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
          N1           N2
============ ============
         111          222

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

