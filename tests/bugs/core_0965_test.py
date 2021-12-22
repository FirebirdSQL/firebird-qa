#coding:utf-8
#
# id:           bugs.core_0965
# title:        Many aggregate functions within a single select list may cause a server crash
# decription:   This test may crash the server.
# tracker_id:   CORE-965
# min_versions: []
# versions:     3.0
# qmid:         bugs.core_965-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """create table tagg (col varchar(30000)) ;

insert into tagg (col) values ('0123456789') ;
commit ;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """select 1 from (
  select col as f1, min(col) as f2, max(col) as f3
   from tagg
  group by 1
) ;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CONSTANT
============
           1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

