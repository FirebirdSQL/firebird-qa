#coding:utf-8
#
# id:           bugs.core_1693
# title:        Error in EXECUTE STATEMENT inside CONNECT / TRANSACTION START triggers
# decription:   
# tracker_id:   CORE-1693
# min_versions: []
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """set term ^ ;

create trigger t_connect on connect
as
  declare v integer;
begin
 execute statement 'select 1 from rdb$database' into v;
end ^

set term ; ^
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """select 1 from rdb$database;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CONSTANT
============
           1

"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

