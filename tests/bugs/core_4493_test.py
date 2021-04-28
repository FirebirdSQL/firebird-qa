#coding:utf-8
#
# id:           bugs.core_4493
# title:        Index not found for RECREATE TRIGGER
# decription:   
# tracker_id:   CORE-4493
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
    recreate table mvt(id int primary key, ac int, amount numeric(12,2));
    recreate table account(id int primary key, balance numeric(12,2));
    commit;
    
    set term ^;
    recreate trigger tai_mvt active after insert or update position 1 on mvt as
    begin
        update account a set a.balance = a.balance + new.amount
        where a.id = new.ac;
    end
    ^
    set term ;^
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.execute()

