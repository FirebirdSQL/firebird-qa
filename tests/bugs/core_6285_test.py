#coding:utf-8

"""
ID:          issue-6527
ISSUE:       6527
TITLE:       SQL-level replication management
DESCRIPTION:
  Test only verifies ability to use statements described in the ticket.
NOTES:
[28.10.2020]
  Replaced 'ADD ... to publication' and 'DROP ... from publication' with
  'INCLUDE ...' and 'EXCLUDE ...' respectively (after reply from dimitr).
JIRA:        CORE-6285
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
     set list on;
     set bail on;
     set count on;
     -- set echo on;
     recreate table test1(id int primary key, x int);
     recreate table test2(id int primary key, x int);
     recreate table test3(id int primary key, x int);
     commit;

     select 'rdb$pub: initial content for a NEW database' as msg, p.* from RDB$PUBLICATIONS p;
     alter database enable publication;
     commit;
     select 'rdb$pub after enable for the WHOLE DATABASE' as msg, p.* from RDB$PUBLICATIONS p;

     alter database disable publication;
     commit;
     select 'rdb$pub after disable for the WHOLE DATABASE' as msg, p.* from RDB$PUBLICATIONS p;
     commit;

     alter database include all to publication;
     commit;
     select 'rdb$pub after ADD ALL tables to publication' as msg, p.* from RDB$PUBLICATION_TABLES p;


     alter database exclude all from publication;
     commit;
     select 'rdb$pub after DROP ALL tables from publication' as msg, p.* from rdb$database left join RDB$PUBLICATION_TABLES p on 1=1;


     alter database include table test2, test3 to publication;
     commit;
     select 'rdb$pub after ADD LIST of some tables to publication' as msg, p.* from RDB$PUBLICATION_TABLES p;

     alter database exclude table test2, test3 from publication;
     commit;
     select 'rdb$pub after DROP LIST of some tables from publication' as msg, p.* from  rdb$database left join RDB$PUBLICATION_TABLES p on 1=1;
"""

act = isql_act('db', test_script)

expected_stdout = """
    MSG                             rdb$pub: initial content for a NEW database
    RDB$PUBLICATION_NAME            RDB$DEFAULT
    RDB$OWNER_NAME                  SYSDBA
    RDB$SYSTEM_FLAG                 1
    RDB$ACTIVE_FLAG                 0
    RDB$AUTO_ENABLE                 0
    Records affected: 1

    MSG                             rdb$pub after enable for the WHOLE DATABASE
    RDB$PUBLICATION_NAME            RDB$DEFAULT
    RDB$OWNER_NAME                  SYSDBA
    RDB$SYSTEM_FLAG                 1
    RDB$ACTIVE_FLAG                 1
    RDB$AUTO_ENABLE                 0
    Records affected: 1

    MSG                             rdb$pub after disable for the WHOLE DATABASE
    RDB$PUBLICATION_NAME            RDB$DEFAULT
    RDB$OWNER_NAME                  SYSDBA
    RDB$SYSTEM_FLAG                 1
    RDB$ACTIVE_FLAG                 0
    RDB$AUTO_ENABLE                 0
    Records affected: 1

    MSG                             rdb$pub after ADD ALL tables to publication
    RDB$PUBLICATION_NAME            RDB$DEFAULT
    RDB$TABLE_NAME                  TEST1
    MSG                             rdb$pub after ADD ALL tables to publication
    RDB$PUBLICATION_NAME            RDB$DEFAULT
    RDB$TABLE_NAME                  TEST2
    MSG                             rdb$pub after ADD ALL tables to publication
    RDB$PUBLICATION_NAME            RDB$DEFAULT
    RDB$TABLE_NAME                  TEST3
    Records affected: 3

    MSG                             rdb$pub after DROP ALL tables from publication
    RDB$PUBLICATION_NAME            <null>
    RDB$TABLE_NAME                  <null>
    Records affected: 1

    MSG                             rdb$pub after ADD LIST of some tables to publication
    RDB$PUBLICATION_NAME            RDB$DEFAULT
    RDB$TABLE_NAME                  TEST2

    MSG                             rdb$pub after ADD LIST of some tables to publication
    RDB$PUBLICATION_NAME            RDB$DEFAULT
    RDB$TABLE_NAME                  TEST3
    Records affected: 2

    MSG                             rdb$pub after DROP LIST of some tables from publication
    RDB$PUBLICATION_NAME            <null>
    RDB$TABLE_NAME                  <null>
    Records affected: 1
"""

@pytest.mark.version('>=4.0.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute()
    assert act.clean_stdout == act.clean_expected_stdout
