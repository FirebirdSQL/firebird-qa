#coding:utf-8
#
# id:           functional.arno.optimizer.opt_full_join_03
# title:        FULL OUTER JOIN,  list all values, but filtered in WHERE clause
# decription:   
#                  TableX FULL OUTER JOIN TableY with relation in the ON clause.
#                  Three tables are used, where 1 table (RC) holds references to the two other tables (R and C). 
#                  The two tables R and C contain both 1 value that isn't inside RC.
#                  =====
#                  Refactored 01-mar-2016. Checked on: WI-V2.5.6.26970, WI-V3.0.0.32366
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         functional.arno.optimizer.opt_full_join_03

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  import time
#  import subprocess
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  engine = str(db_conn.engine_version)
#  db_conn.close()
#  
#  sql_cmd='''
#      create table relations (
#          relationid integer,
#          relationname varchar(35)
#      );
#      
#      create table categories (
#          categoryid integer,
#          description varchar(20)
#      );
#      
#      create table relationcategories (
#          relationid integer,
#          categoryid integer
#      );
#      commit;
#      
#      insert into relations (relationid, relationname) values (1, 'diving snorkel shop');
#      insert into relations (relationid, relationname) values (2, 'bakery garbage');
#      insert into relations (relationid, relationname) values (3, 'racing turtle');
#      insert into relations (relationid, relationname) values (4, 'folding air-hook shop');
#      
#      insert into categories (categoryid, description) values (1, 'relation');
#      insert into categories (categoryid, description) values (2, 'debtor');
#      insert into categories (categoryid, description) values (3, 'creditor');
#      insert into categories (categoryid, description) values (4, 'newsletter');
#      
#      insert into relationcategories (relationid, categoryid) values (1, 1);
#      insert into relationcategories (relationid, categoryid) values (2, 1);
#      insert into relationcategories (relationid, categoryid) values (3, 1);
#      insert into relationcategories (relationid, categoryid) values (1, 2);
#      insert into relationcategories (relationid, categoryid) values (2, 2);
#      insert into relationcategories (relationid, categoryid) values (1, 3);
#      
#      commit;
#      
#      -- Normally these indexes are created by the primary/foreign keys,
#      -- but we don't want to rely on them for this test
#      create unique asc index pk_relations on relations (relationid);
#      create unique asc index pk_categories on categories (categoryid);
#      create unique asc index pk_relationcategories on relationcategories (relationid, categoryid);
#      create asc index fk_rc_relations on relationcategories (relationid);
#      create asc index fk_rc_categories on relationcategories (categoryid);
#      
#      commit;
#  
#  
#      set plan on;
#      set list on;
#      -- full join should return ...
#      select
#          r.relationname,
#          rc.relationid,
#          rc.categoryid,
#          c.description
#      from
#          relations r
#          full join relationcategories rc on (rc.relationid = r.relationid)
#          full join categories c on (c.categoryid = rc.categoryid)
#      where
#          c.categoryid >= 2
#      order by
#          rc.categoryid desc;
#  '''
#  
#  f_sql=open( os.path.join(context['temp_directory'],'tmp_opt_full_join_03.tmp'), 'w')
#  f_sql.write(sql_cmd)
#  f_sql.close()
#  
#  f_log = open( os.path.join(context['temp_directory'],'tmp_opt_full_join_03.log'), 'w')
#  
#  subprocess.call( [context['isql_path'], dsn, "-i", f_sql.name],
#                   stdout=f_log,
#                   stderr=subprocess.STDOUT
#                 )
#  f_log.close()
#  time.sleep(1)
#  
#  plan_25 = 'PLAN SORT (JOIN (C INDEX (PK_CATEGORIES), JOIN (RC NATURAL, R NATURAL)))'
#  plan_30 = 'PLAN SORT (JOIN (JOIN (C INDEX (PK_CATEGORIES), JOIN (JOIN (RC NATURAL, R INDEX (PK_RELATIONS)), JOIN (R NATURAL, RC INDEX (FK_RC_RELATIONS)))), JOIN (JOIN (JOIN (RC NATURAL, R INDEX (PK_RELATIONS)), JOIN (R NATURAL, RC INDEX (FK_RC_RELATIONS))), C INDEX (PK_CATEGORIES))))'
#  with open(f_log.name) as f:
#      for line in f:
#          if line.upper().startswith('PLAN '):
#              if engine.startswith('2.'):
#                  plan_expected=plan_25
#              else:
#                  plan_expected=plan_30
#  
#              # Remove trailing whitespaces and newline character:
#              if line.upper().rstrip() == plan_expected:
#                  print( 'Actual plan plan coincides with the expected.' )
#              else:
#                  print( 'Actual plan: '+line+' - differs from expected: '+plan_expected)
#          else:
#              print(line )
#  
#  # Cleanup
#  #########
#  os.remove(f_log.name)
#  os.remove(f_sql.name)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Actual plan plan coincides with the expected.

    RELATIONNAME                    diving snorkel shop
    RELATIONID                      1
    CATEGORYID                      3
    DESCRIPTION                     creditor
    RELATIONNAME                    diving snorkel shop
    RELATIONID                      1
    CATEGORYID                      2
    DESCRIPTION                     debtor
    RELATIONNAME                    bakery garbage
    RELATIONID                      2
    CATEGORYID                      2
    DESCRIPTION                     debtor
    RELATIONNAME                    <null>
    RELATIONID                      <null>
    CATEGORYID                      <null>
    DESCRIPTION                     newsletter
  """

@pytest.mark.version('>=2.5')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


