#coding:utf-8

"""
ID:          issue-7899
ISSUE:       7899
TITLE:       Inconsistent state of master-detail occurs after RE-connect + 'SET AUTODDL OFF' + 'drop <FK>' which is ROLLED BACK
DESCRIPTION:
NOTES:
    Confirmed bug on 6.0.0.180.
    Checked on intermediate builds:
         6.0.0.186,  commit 305c40a05b1d64c14dbf5f25f36c42c44c6392d9
         5.0.1.1307, commit e35437e00687db9ed6add279cecb816dcdf8b07a
         4.0.5.3042, commit f7b090043e8886ab6286f8d626dd1684dc09e3b8
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "TDETL_FK" on table "PERSISTENT_DETL"
    -Foreign key reference target does not exist
    -Problematic key value is ("ID" = 1)

    Statement failed, SQLSTATE = 23000
    violation of FOREIGN KEY constraint "TDETL_FK" on table "PERSISTENT_DETL"
    -Foreign key reference target does not exist
    -Problematic key value is ("ID" = 2)
"""

@pytest.mark.version('>=4.0.5')
def test_1(act: Action):

    test_script = f"""
        set list on;
        create table persistent_main (
            id int not null,
            primary key (id)
        );
         
        create table persistent_detl (id int);
         
        alter table persistent_detl add constraint tdetl_fk foreign key (id) references persistent_main (id);
        commit;
         
        insert into persistent_detl(id) values(1);
        commit;
         
        connect '{act.db.dsn}'; -------------------------------------------------------- [ !!! 1 !!! ] 
         
        set autoddl off;
        commit;
         
        alter table persistent_detl drop constraint tdetl_fk;

        rollback; -------------------------------------------------------- [ !!! 2 !!! ] 
         
         
        insert into persistent_detl(id) values(2);
         
        select d.id as orphan_child_id
        from persistent_detl d
        where not exists(select * from persistent_main m where m.id = d.id);
    """

    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
