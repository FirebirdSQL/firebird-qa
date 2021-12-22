#coding:utf-8
#
# id:           bugs.core_3038
# title:        Wrong resultset
# decription:   The insert failed because a column definition includes validation constraints. validation error for variable
# tracker_id:   CORE-3038
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    create domain money as numeric(15,4);
    commit;

    create table cl_cashprice (id integer not null, price money not null);
    commit;

    set term ^ ;
    create procedure testp (i_id integer, i_price type of column cl_cashprice.price)
    as
      declare variable goodsprice money;
    begin
      goodsprice = null;
      if (:goodsprice is not null)
        then goodsprice = 6;
    end^
    set term ; ^
    commit;

    execute procedure testp(1, 6);
    commit; 
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.execute()

