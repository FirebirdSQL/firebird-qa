#coding:utf-8
#
# id:           bugs.core_3883
# title:        Ambiguous field name in the trigger when it does a select from the table
# decription:   
# tracker_id:   CORE-3883
# min_versions: ['2.0.7']
# versions:     2.0.7
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.0.7
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table regtype (
        code_regtype int constraint pk_regtype primary key,
        name varchar(20),
        multirecord smallint
    );
    
    recreate table reg (
        code_reg int constraint pk_reg primary key,
        code_regtype int,
        code_horse int
    );

    create exception e_duplicate_reg 'duplicate registration info';
    
    set term ^ ;
    create or alter trigger reg_bi0 for reg
    active before insert position 0 as
    begin
      if (exists(select 1
                 from reg
                      inner join regtype on reg.code_regtype = regtype.code_regtype
                 where reg.code_horse = new.code_horse and
                       reg.code_regtype = new.code_regtype and
                       regtype.multirecord = 0)) then
        exception e_duplicate_reg;
    end
    ^
    set term ;^
    commit;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.0.7')
def test_1(act_1: Action):
    act_1.execute()

