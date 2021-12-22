#coding:utf-8
#
# id:           bugs.core_3461
# title:        DDL operations fail after backup/restore
# decription:   
# tracker_id:   CORE-3461
# min_versions: ['2.5.1']
# versions:     2.5.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core3461.fbk', init=init_script_1)

test_script_1 = """
    set autoddl off;
    set term ^ ;
    drop table test_tbl ^
    alter procedure test_proc(id integer) as begin end ^
    alter table test_tbl2 add id2 integer ^
    alter procedure test_tbl_proc as
    declare id integer;
    declare id2 integer;
    begin
      select id, id2 from test_tbl2 into :id, :id2;
    end ^
    commit^
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)


@pytest.mark.version('>=2.5.1')
def test_1(act_1: Action):
    act_1.execute()

