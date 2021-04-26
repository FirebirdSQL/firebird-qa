#coding:utf-8
#
# id:           bugs.core_2264
# title:        ALTER DOMAIN with dependencies may leave a transaction handle in inconsistent state causing segmentation faults
# decription:   
# tracker_id:   CORE-2264
# min_versions: []
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    create domain d int;
    set term ^;
    create or alter procedure p1 as
      declare v d;
    begin
      v = v + v;
    end
    ^
    set term ;^
    commit;
    alter domain d type varchar(11);
    alter domain d type varchar(11); -- segmentation fault here
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_core_2264_1(act_1: Action):
    act_1.execute()

