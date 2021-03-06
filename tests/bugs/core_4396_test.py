#coding:utf-8
#
# id:           bugs.core_4396
# title:        incorrect result query if it is execute through "execute statement"
# decription:   
#                   Checked on:
#                       4.0.0.1635 SS: 1.091s.
#                       4.0.0.1633 CS: 1.367s.
#                       3.0.5.33180 SS: 0.795s.
#                       3.0.5.33178 CS: 1.015s.
#                
# tracker_id:   CORE-4396
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
    recreate table test(run smallint, rn smallint, id int);
    commit;
    
    insert into test(run, rn, id)
    select 1, row_number()over(), r.rdb$relation_id
    from rdb$relations r
    order by rdb$relation_id rows 3;
    commit;
    
    set term ^;
    execute block returns ( id integer ) as
        declare r int;
        declare i int;
    begin
        for
            execute statement
                'select row_number()over(), rdb$relation_id from rdb$relations order by rdb$relation_id rows 3'
            on external 'localhost:' || rdb$get_context('SYSTEM','DB_NAME')
                as user 'sysdba' password 'masterkey'
            into r, i
        do insert into test(run, rn, id) values(2, :r, :i);
    end
    ^
    set term ;^
    commit;
    
    set list on;
    select count(*) cnt
    from (
        select rn,id --,min(run),max(run)
        from test
        group by 1,2
        having max(run)-min(run)<>1
    ) x;
    commit;

    --                                    ||||||||||||||||||||||||||||
    -- ###################################|||  FB 4.0+, SS and SC  |||##############################
    --                                    ||||||||||||||||||||||||||||
    -- If we check SS or SC and ExtConnPoolLifeTime > 0 (config parameter FB 4.0+) then current
    -- DB (bugs.core_NNNN.fdb) will be 'captured' by firebird.exe process and fbt_run utility
    -- will not able to drop this database at the final point of test.
    -- Moreover, DB file will be hold until all activity in firebird.exe completed and AFTER this
    -- we have to wait for <ExtConnPoolLifeTime> seconds after it (discussion and small test see
    -- in the letter to hvlad and dimitr 13.10.2019 11:10).
    -- This means that one need to kill all connections to prevent from exception on cleanup phase:
    -- SQLCODE: -901 / lock time-out on wait transaction / object <this_test_DB> is in use
    -- #############################################################################################
    delete from mon$attachments where mon$attachment_id != current_connection;
    commit;    
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CNT                             0
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

