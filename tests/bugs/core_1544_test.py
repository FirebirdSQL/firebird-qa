#coding:utf-8
#
# id:           bugs.core_1544
# title:        RDB$procedures generator overflow
# decription:
# tracker_id:
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
    -- ::: WARNING ::: This code executes about ~3-4 minutes on Pentium 3.0 GHz with SATA HDD
    set term ^;
    execute block as
        declare i int = 0;
        declare n int = 32839;
    begin
        while (i<n) do
        begin
            in autonomous transaction do
            execute statement 'create or alter procedure p' || i || ' as begin end';

            in autonomous transaction do
            execute statement 'drop procedure p' || i;
            i = i + 1;
        end
    end
    ^
    set term ;^
    commit; -- at this point value of generator `rdb$procedures` is 32840
    create procedure aux_sp1 as begin end;
    create procedure aux_sp2 as begin end;
    commit;
    set list on;
    select gen_id(rdb$procedures,0) gen_rdb_proc_curr_value from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    GEN_RDB_PROC_CURR_VALUE         32842
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

