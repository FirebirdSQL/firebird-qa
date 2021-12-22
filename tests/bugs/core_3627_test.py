#coding:utf-8
#
# id:           bugs.core_3627
# title:        Server crashes with access violation when inserting row into table with unique index
# decription:   
# tracker_id:   CORE-3627
# min_versions: ['2.5.3']
# versions:     2.5.3
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.3
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Confirmed crash on WI-V2.5.1.26351:
    -- Statement failed, SQLSTATE = 08006
    -- Unable to complete network request to host "localhost".
    -- -Error reading data from the connection.

    recreate table testtable
    (
      "ID" integer not null,
      "CLASSID" integer,
      primary key ("ID")
    );
    insert into TestTable values(1, 1);
    insert into TestTable values(2, 2);
    commit;
    
    alter table testtable add ksgfk integer;
    create unique index classidksgidx on testtable (classid, ksgfk);
    
    insert into testtable values(3,1,null);
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = 23000
    attempt to store duplicate value (visible to active transactions) in unique index "CLASSIDKSGIDX"
    -Problematic key value is ("CLASSID" = 1, "KSGFK" = NULL)
"""

@pytest.mark.version('>=2.5.3')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_stderr == act_1.clean_expected_stderr

