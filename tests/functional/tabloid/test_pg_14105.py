#coding:utf-8
#
# id:           functional.tabloid.pg_14105
# title:        Check ability to compile query with combination of full and right join. Taken from PG bug library.
# decription:   
#                  Original issue ( http://www.postgresql.org/message-id/20160420194758.22924.80319@wrigleys.postgresql.org ):
#                  ===
#                     create table a as (select 1 as id);
#                     select *
#                     from ((
#                            a as a1
#                            full join (select 1 as id) as tt
#                            on (a1.id = tt.id)
#                           )
#                           right join (select 1 as id) as tt2
#                           on (coalesce(tt.id) = tt2.id)
#                          )
#                     ;
#                     ERROR:  XX000: failed to build any 2-way joins
#                     LOCATION:  standard_join_search, allpaths.c:1832
#               
#               
#                     It works on PostgreSQL 9.2.13., returning:
#                      id | id | id 
#                     ----+----+----
#                       1 |  1 |  1
#                     (1 row)
#                   ===
#                   PS. NOTE on strange form of COALESCE: "coalesce(tt.id)" - it has only single argument.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    recreate table a(id int);
    commit;

    insert into a values(1);
    commit;

    set list on;

    select *
    from (
        select a1.id as a1_id, tt.id as tt_id, tt2.id as tt2_id
        from 
            (
               a as a1
               full join ( select 1 as id from rdb$database ) as tt 
                    on ( a1.id = tt.id )
            )
            right join (select 1 as id from rdb$database) as tt2
            	  -- https://www.drupal.org/node/336712
                  --  When used with one argument, it will return NULL if that argument is NULL; 
                  -- therefore, in such cases, using it is perfectly useless.
                  on ( coalesce(tt.id,tt.id) = tt2.id )
    )
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    A1_ID                           1
    TT_ID                           1
    TT2_ID                          1
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

