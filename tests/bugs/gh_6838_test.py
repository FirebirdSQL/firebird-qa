#coding:utf-8
#
# id:           bugs.gh_6838
# title:        Deleting multiple rows from a view with triggers may cause triggers to fire just once
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6838
#               
#                   Confirmed bug on 4.1.0.2468, 5.0.0.56.
#                   Checked on intermediate builds 4.0.0.2506, 5.0.0.60 (bith have timestamp: 02.06.2021 15:12) -- all OK.
#                
# tracker_id:   
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    create table t (id int);
    create view v as select id from t;
    create table log (txt varchar(10));

    set term ^;
    create trigger trg for v before update or delete as
    begin
        insert into log values ( iif(deleting, 'deleted', 'updated') );
    end
    ^
    set term ;^

    insert into t values (1);
    insert into t values (2);
    commit;

    delete from v;
    set count on;
    select * from log;
    set count off;
    rollback;

    merge into v t
    using v s on s.id = t.id
    when matched then delete;

    set count on;
    select * from log;
    set count off;
    rollback;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TXT                             deleted
    TXT                             deleted
    Records affected: 2

    TXT                             deleted
    TXT                             deleted
    Records affected: 2
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
