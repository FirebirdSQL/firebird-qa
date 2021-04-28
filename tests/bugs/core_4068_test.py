#coding:utf-8
#
# id:           bugs.core_4068
# title:        create package fails on creating header as soon as there is at least 1 procedure name
# decription:   
# tracker_id:   CORE-4068
# min_versions: ['3.0']
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
    set term ^;
    create or alter package fb$out
    as
    begin
    procedure enable;
    end
    ^
    set term ;^
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

