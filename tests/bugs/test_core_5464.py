#coding:utf-8
#
# id:           bugs.core_5464
# title:        AV in fbclient when reading blob stored in incompatible encoding
# decription:   
#                  Reproduced crash of isql on WI-T4.0.0.463
#                  (standard message appeared with text about program that is to be closed).
#                  Checked on 3.0.2.32677, 4.0.0.519 - works fine.
#                
# tracker_id:   CORE-5464
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """
    create domain d_int int;
    comment on domain d_int is
    '*Лев Николаевич Толстой * *Анна Каренина * /Мне отмщение, и аз воздам/ *ЧАСТЬ ПЕРВАЯ* *I *
    Все счастливые семьи похожи друг на друга, каждая несчастливая 
    семья несчастлива по-своему. 
    Все смешалось в доме Облонских. Жена узнала, что муж был в связи
    с бывшею в их доме француженкою-гувернанткой, и объявила мужу, что
    не может жить с ним в одном доме. Положение это продолжалось уже
    третий день и мучительно чувствовалось и самими супругами, и всеми
    членами семьи, и домочадцами. Все члены семьи и домочадцы
    чувствовали, что нет смысла в их сожительстве и что на каждом
    п1
    ';
    commit;  
  """

db_1 = db_factory(charset='WIN1251', sql_dialect=3, init=init_script_1)

# test_script_1
#---
# 
#  import os
#  import sys
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#  
#  so=sys.stdout
#  se=sys.stderr
#  
#  fn_log = os.path.join(context['temp_directory'],'tmp_c5464.log')
#  fn_err = os.path.join(context['temp_directory'],'tmp_c5464.err')
#  sys.stdout = open( fn_log, 'w')
#  sys.stderr = open( fn_err, 'w')
#  sql='''
#      set names win1250;
#      connect '%s' user '%s' password '%s';
#      set blob all;
#      set list on;
#  
#      select c.rdb$character_set_name as connection_cset, r.rdb$character_set_name as db_default_cset
#      from mon$attachments a
#      join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
#      cross join rdb$database r where a.mon$attachment_id=current_connection;
#      
#      select rdb$field_name, rdb$system_flag, rdb$description 
#      from rdb$fields where rdb$description is not null; 
#  ''' % ( dsn, user_name, user_password  )
#  
#  runProgram('isql',['-q'],sql)
#  
#  sys.stdout = so
#  sys.stderr = se
#  
#  with open( fn_log,'r') as f:
#    for line in f:
#      line=line.replace('SQL> ', '').replace('CON> ', '').rstrip()
#      if line.split():
#        print(line)
#  
#  with open( fn_err,'r') as f:
#    for line in f:
#      if line.split():
#        print(line)
#  
#  os.remove(fn_log)
#  os.remove(fn_err)
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    CONNECTION_CSET                 WIN1250
    DB_DEFAULT_CSET                 WIN1251
    Statement failed, SQLSTATE = 22018
    Cannot transliterate character between character sets  
  """

@pytest.mark.version('>=3.0.2')
@pytest.mark.xfail
def test_core_5464_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


