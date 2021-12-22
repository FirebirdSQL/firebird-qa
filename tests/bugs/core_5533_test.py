#coding:utf-8
#
# id:           bugs.core_5533
# title:        Crash on 3.0 and 4.0 when DB contains database-level trigger
# decription:   
#                  Confirmed bug on WI-T4.0.0.633.
#                  Checked on WI-T4.0.0.638, WI-V3.0.3.32721 -- both on SS and CS.
#                
# tracker_id:   CORE-5533
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set bail on;
    set list on;
    set term ^;
    execute block as
    begin
        begin
            execute statement 'drop trigger trg_tx_start';
        when any do begin end
        end
    end
    ^
    set term ;^
    commit;

    recreate table tlog (ID integer default current_transaction, msg varchar(20));

    set term ^;
    create trigger trg_tx_start inactive on transaction start position 0
    as
    begin
      execute statement ('insert into tlog(msg) values(?)') ('Tx start');
    end
    ^
    set term ;^
    commit;

    set autoddl off;
    select count(distinct id) id_distinct_count_0 from tlog;
    alter trigger trg_tx_start active;
    commit;

    set term ^;
    execute block as
        declare c int;
    begin
        begin
            execute statement 'drop trigger trg_tx_start';
        when any do begin end
        end
    end
    ^
    set term ;^
    commit;

    select count(distinct id) id_distinct_count_1 from tlog;
    commit;
    select count(distinct id) id_distinct_count_2 from tlog;
    quit; 

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ID_DISTINCT_COUNT_0             0
    ID_DISTINCT_COUNT_1             1
    ID_DISTINCT_COUNT_2             1
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

