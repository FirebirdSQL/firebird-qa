#coding:utf-8
#
# id:           bugs.gh_6963
# title:        grant references not working
# decription:   
#                   https://github.com/FirebirdSQL/firebird/issues/6963
#                   
#                   Confirmed bug on 4.0.1.2658, 5.0.0.309.
#                   Checked on 4.0.1.2660, 5.0.0.310 -- all fine.
#               
#                
# tracker_id:   
# min_versions: ['4.0.1']
# versions:     4.0.1
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.1
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table tmain_a(
        id int primary key
       ,pid int
    );

    commit;

    create or alter user tmp$gh6963 password '123' using plugin Srp;
    grant select,references on tmain_a to tmp$gh6963;
    grant create table to tmp$gh6963; -- NB: do NOT grant rights to ALTER any and DROP any table!

    commit;
    connect '$(DSN)' user tmp$gh6963 password '123';

    alter table tmain_a add constraint test_fk_self_without_casc
        foreign key(pid) references tmain_a(id)
    ;

    -- must FAIL because current non-privileged user is NOT owner of 'tmain_a' table:
    alter table tmain_a add constraint test_fk_self_with_cascade
        foreign key(pid) references tmain_a(id)
        on update cascade on delete cascade
    ;

    -- ##################################################
    -- Following two statements must pass because user 'tmp$gh6963' has right to create table
    -- and add FK in it with reference to another table (for which he is not owner), no matter
    -- is this FK defined with or without CASCADE option:
    -- ##################################################
    -- 1. This WORKED before fix:
    create table tdetl_a_without_casc(
        id int primary key,
        pid int,
        foreign key(id) references tmain_a(id)
    );

    -- 2. This DID NOT work before fix, failed with:
    -- Statement failed, SQLSTATE = 28000
    -- unsuccessful metadata update
    -- -CREATE TABLE TDETL_A_WITH_CASC failed
    -- -no permission for ALTER access to TABLE TMAIN_A
    -- -Effective user is TMP$GH6963
    create table tdetl_a_with_casc(
        id int primary key,
        pid int,
        foreign key(id) references tmain_a(id)
            on update cascade on delete cascade
    );

    commit;
    connect '$(DSN)' user sysdba password 'masterkey';

    set list on;
    set count on;
    select rdb$relation_name
    from rdb$relations
    where
        rdb$relation_name starting with upper('tmain_') or
        rdb$relation_name starting with upper('tdetl_')
    order by rdb$relation_name
    ;
    commit;

    drop user tmp$gh6963 using plugin Srp;

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$RELATION_NAME               TDETL_A_WITHOUT_CASC
    RDB$RELATION_NAME               TDETL_A_WITH_CASC
    RDB$RELATION_NAME               TMAIN_A
    Records affected: 3
"""
expected_stderr_1 = """
    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TMAIN_A failed
    -no permission for ALTER access to TABLE TMAIN_A
    -Effective user is TMP$GH6963

    Statement failed, SQLSTATE = 28000
    unsuccessful metadata update
    -ALTER TABLE TMAIN_A failed
    -no permission for ALTER access to TABLE TMAIN_A
    -Effective user is TMP$GH6963
"""

@pytest.mark.version('>=4.0.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr
    assert act_1.clean_stdout == act_1.clean_expected_stdout
