#coding:utf-8
#
# id:           bugs.core_6285
# title:        SQL-level replication management
# decription:   
#                   Test only verifies ability to use statements described in the ticket.
#                   Checked on 4.0.0.1920.
#               
#                   28.10.2020
#                   Replaced 'ADD ... to publication' and 'DROP ... from publication' with
#                   'INCLUDE ...' and 'EXCLUDE ...' respectively (after reply from dimitr).
#                   Checked on 4.0.0.2240.
#                
# tracker_id:   CORE-6285
# min_versions: []
# versions:     4.0.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
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

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
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
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

