#coding:utf-8
#
# id:           bugs.core_0986
# title:        Non-ASCII quoted identifiers are not converted to metadata (UNICODE_FSS) charset
# decription:   
#                   Test prepares file that will serve as input SQL script and will have CYRYLLIC names for all
#                   database objects: collations, domains, exceptions, tables, views etc.
#                   File has name = 'tmp_non_ascii_ddl_0986.sql' and is encoded to windows-1251 codepage.
#                   Then we:
#                   1. Attempt to apply this file in ISQL __WITHOUT__ specifying charset and with 'set bail on'.
#                      This action should IMMEDIATELY be denied (i.e. no objects should be created in database at all).
#                      Also, two logs should be created for this attempt:
#                           1.1) STDOUT with first (and single) statement that ISQL was to be executed;
#                           1.2) STDERR with single exception, it depends on major FB version:
#                               * for FB 3.x: SQLSTATE = 22000 / malformed string;
#                               * for FB 4.x: SQLSTATE = 22018 / Cannot transliterate ...
#               
#                   2. Attempt to apply the same script but now _WITH_ specification of connect charset: -ch win1251.
#                      This attempt should finish SUCCESSFULLY, and we will verify it by checking its:
#                           2.1) STDOUT - it should contain phrase "Metadata created OK."
#                           2.2) STDERR - it should be EMPTY.
#                   
#                   Confirmed on 2.0.7: one might to run ISQL without specifying '-ch XXXX' switch and give it
#                   script which 
#                   1) was encoded in NON unicode character set (e.g. win1251 - as is used in this test) and 
#                   2) did create DB objects with non-ascii names.
#                   
#                   Checked on:
#                       4.0.0.1635 SS: 3.217s.
#                       4.0.0.1633 CS: 3.619s.
#                       3.0.5.33180 SS: 2.548s.
#                       3.0.5.33178 CS: 3.153s.
#               
#               	17-mar-2021. Re-implemented in order to have ability to run this test on Linux.
#               	Ttest creates table and fills it with non-ascii characters in init_script, using charset = UTF8.
#               	Then it generates .sql script for running it in separae ISQL process.
#               	This script makes connection to test DB using charset = WIN1251 and perform needed DML.
#               	Result will be redirected to .log which will be opened via codecs.open(...encoding='cp1251').
#               	Its content will be converted to UTF8 for further parsing.
#               	
#               	Checked on:
#               		* Windows: 4.0.0.2387, 3.0.8.33426
#               		* Linux:   4.0.0.2387, 3.0.8.33426
#                       
#                
# tracker_id:   CORE-0986
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

# test_script_1
#---
# import os
#  import time
#  import subprocess
#  
#  # 28.10.2019. This is needed in Python 2.7 for converting string in UTF8 to cp1251
#  import codecs
#  
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  
#  #--------------------------------------------
#  
#  def flush_and_close( file_handle ):
#      # https://docs.python.org/2/library/os.html#os.fsync
#      # If you're starting with a Python file object f,
#      # first do f.flush(), and
#      # then do os.fsync(f.fileno()), to ensure that all internal buffers associated with f are written to disk.
#      global os
#  
#      file_handle.flush()
#      if file_handle.mode not in ('r', 'rb') and file_handle.name != os.devnull:
#          # otherwise: "OSError: [Errno 9] Bad file descriptor"!
#          os.fsync(file_handle.fileno())
#      file_handle.close()
#  
#  #--------------------------------------------
#  
#  def cleanup( f_names_list ):
#      global os
#      for i in range(len( f_names_list )):
#         if type(f_names_list[i]) == file:
#            del_name = f_names_list[i].name
#         elif type(f_names_list[i]) == str:
#            del_name = f_names_list[i]
#         else:
#            print('Unrecognized type of element:', f_names_list[i], ' - can not be treated as file.')
#            del_name = None
#  
#         if del_name and os.path.isfile( del_name ):
#             os.remove( del_name )
#  
#  #--------------------------------------------
#  
#  
#  # Obtain engine version:
#  cur1 = db_conn.cursor()
#  cur1.execute("select rdb$get_context('SYSTEM','ENGINE_VERSION') as engine_version from rdb$database")
#  for row in cur1:
#      engine = row[0]
#  
#  db_conn.close()
#  
#  non_ascii_ddl='''
#      set bail on;
#  
#      -- set names win1251;
#      connect '%(dsn)s' user '%(user_name)s' password '%(user_password)s';
#      
#      set echo on;
#  
#      create collation "Циферки" for utf8 from unicode case insensitive 'NUMERIC-SORT=1';
#      create collation "Испания" for iso8859_1 from es_es_ci_ai 'SPECIALS-FIRST=1';;
#      commit;
#  
#      create domain "ИД'шники" int;
#      create domain "Группы" varchar(30) check( value in ('Электрика', 'Ходовая', 'Арматурка', 'Кузовщина') );
#      create domain "Артикулы" varchar(12) character set utf8 check( value = upper(value) ) 
#      collate "Циферки" -- enabled since core-5220 was fixed (30.04.2016)
#      ;
#      create domain "Комрады" varchar(40) character set iso8859_1 
#      collate "Испания" -- enabled since core-5220 was fixed (30.04.2016)
#      ;
#      create domain "Кол-во" numeric(12,3) not null;
#  
#      create sequence generilka;
#      create sequence "Генерилка";
#  
#      create role "манагер";
#      create role "начсклд";
#  
#      -- TEMPLY COMMENTED UNTIL CORE-5209 IS OPEN:
#      -- ISQL -X ignores connection charset for text of EXCEPTION message (restoring it in initial charset when exception was created)
#      recreate exception "Невзлет" 'Запись обломалась, ваши не пляшут. Но не стесняйтесь и обязательно заходите еще, мы всегда рады видеть вас. До скорой встречи, товарищ!';
#      commit;
#  	
#      -------------------------------------------------
#      recreate table "склад" (
#           "ИД'шник" "ИД'шники"
#          ,"Откудова" "Группы"
#          ,"Номенклатура" "Артикулы"
#          ,"ИД'родителя" "ИД'шники"
#          ,"сколько там" "Кол-во"
#          ,constraint "ПК-ИД'шник" primary key ("ИД'шник") using index "склад_ПК"
#          ,constraint "ФК-на-родока" foreign key("ИД'родителя") references "склад" ("ИД'шник")  using index "склад_ФК"
#          ,constraint "остаток >=0" check ("сколько там" >= 0)
#      );
#  
#      recreate view "Электрика"("ид изделия", "Название", "Запас") as
#      select 
#           "ИД'шник" 
#          ,"Номенклатура"
#          ,"сколько там"
#      from "склад"
#      where "Откудова" = 'Электрика'
#      ;
#  
#      set term ^;
#      create or alter trigger "склад би" for "склад" active before insert as
#      begin
#          --new."ИД'шник" = coalesce( new."ИД'шник", gen_id(generilka, 1) );
#          -- not avail up to 2.5.6: 
#          new."ИД'шник" = coalesce( new."ИД'шник", gen_id("Генерилка", 1) );
#      end
#      ^
#  
#      create or alter procedure "Доб на склад"(
#           "Откудова" varchar(30)
#          ,"Номенклатура" varchar(30)
#          ,"ИД'родителя" int
#          ,"сколько там" numeric(12,3)
#      ) returns (
#          "код возврата" int
#      ) as
#      begin
#          insert into "склад"(
#               "Откудова"
#              ,"Номенклатура"
#              ,"ИД'родителя" 
#              ,"сколько там"
#          ) values (
#               :"Откудова"
#              ,:"Номенклатура"
#              ,:"ИД'родителя" 
#              ,:"сколько там"
#          );
#          
#      end
#      ^
#      create or alter procedure "Удалить" as
#      begin
#       /*
#              Антон Павлович Чехов. Каштанка
#  
#              1. Дурное поведение
#  
#               Молодая рыжая собака - помесь такса с дворняжкой - очень похожая мордой
#          на лисицу, бегала взад и вперед по тротуару  и  беспокойно  оглядывалась  по
#          сторонам. Изредка она останавливалась и, плача, приподнимая то одну  озябшую
#          лапу, то другую, старалась дать себе отчет: как это могло случиться, что она
#          заблудилась?
#       */
#      end
#      ^
#      set term ;^
#  
#      grant select on "склад" to "манагер";
#      grant select, insert, update, delete on "склад" to "начсклд";
#      -- no avail in 2.0: grant execute procedure "Доб на склад" to "начсклд";
#  
#  
#      comment on sequence "Генерилка" is 'Генератор простых идей';
#      comment on table "склад" is 'Это всё, что мы сейчас имеем в наличии';
#      comment on view "Электрика" is 'Не суй пальцы в розетку, будет бо-бо!';
#      comment on procedure "Доб на склад" is 'Процедурка добавления изделия на склад';
#      comment on parameter "Доб на склад"."Откудова" is 'Группа изделия, которое собираемся добавить';
#  
#      comment on parameter "Доб на склад"."ИД'родителя"  is '
#          Федор Михайлович Достоевский
#  
#          Преступление и наказание
#  
#          Роман в шести частях с эпилогом
#            
#  
#          Часть первая
#  
#          I
#         В начале июля, в чрезвычайно жаркое время, под вечер, один молодой человек вышел из своей каморки, которую нанимал от жильцов в С -- м переулке, на улицу и медленно, как бы в нерешимости, отправился к К -- ну мосту. 
#         Он благополучно избегнул встречи с своею хозяйкой на лестнице. Каморка его приходилась под самою кровлей высокого пятиэтажного дома и походила более на шкаф, чем на квартиру. Квартирная же хозяйка его, у которой он нанимал эту каморку с обедом и прислугой, помещалась одною лестницей ниже, в отдельной квартире, и каждый раз, при выходе на улицу, ему непременно надо было проходить мимо хозяйкиной кухни, почти всегда настежь отворенной на лестницу. И каждый раз молодой человек, проходя мимо, чувствовал какое-то болезненное и трусливое ощущение, которого стыдился и от которого морщился. Он был должен кругом хозяйке и боялся с нею встретиться. 
#         Не то чтоб он был так труслив и забит, совсем даже напротив; но с некоторого времени он был в раздражительном и напряженном состоянии, похожем на ипохондрию. Он до того углубился в себя и уединился от всех, что боялся даже всякой встречи, не только встречи с хозяйкой. Он был задавлен бедностью; но даже стесненное положение перестало в последнее время тяготить его. Насущными делами своими он совсем перестал и не хотел заниматься. Никакой хозяйки, в сущности, он не боялся, что бы та ни замышляла против него. Но останавливаться на лестнице, слушать всякий вздор про всю эту обыденную дребедень, до которой ему нет никакого дела, все эти приставания о платеже, угрозы, жалобы, и при этом самому изворачиваться, извиняться, лгать, -- нет уж, лучше проскользнуть как-нибудь кошкой по лестнице и улизнуть, чтобы никто не видал. 
#         Впрочем, на этот раз страх встречи с своею кредиторшей даже его самого поразил по выходе на улицу. 
#         "На какое дело хочу покуситься и в то же время каких пустяков боюсь! -- подумал он с странною улыбкой. -- Гм... да... всё в руках человека, и всё-то он мимо носу проносит, единственно от одной трусости... это уж аксиома... Любопытно, чего люди больше всего боятся? Нового шага, нового собственного слова они всего больше боятся... А впрочем, я слишком много болтаю. Оттого и ничего не делаю, что болтаю. Пожалуй, впрочем, и так: оттого болтаю, что ничего не делаю. Это я в этот последний месяц выучился болтать, лежа по целым суткам в углу и думая... о царе Горохе. Ну зачем я теперь иду? Разве я способен на это? Разве это серьезно? Совсем не серьезно. Так, ради фантазии сам себя тешу; игрушки! Да, пожалуй что и игрушки!" 
#         На улице жара стояла страшная, к тому же духота, толкотня, всюду известка, леса, кирпич, пыль и та особенная летняя вонь, столь известная каждому петербуржцу, не имеющему возможности нанять дачу, -- всё это разом неприятно потрясло и без того уже расстроенные нервы юноши. Нестерпимая же вонь из распивочных, которых в этой части города особенное множество, и пьяные, поминутно попадавшиеся, несмотря на буднее время, довершили отвратительный и грустный колорит картины. Чувство глубочайшего омерзения мелькнуло на миг в тонких чертах молодого человека. Кстати, он был замечательно хорош собою, с прекрасными темными глазами, темно-рус, ростом выше среднего, тонок и строен. Но скоро он впал как бы в глубокую задумчивость, даже, вернее сказать, как бы в какое-то забытье, и пошел, уже не замечая окружающего, да и не желая его замечать. Изредка только бормотал он что-то про себя, от своей привычки к монологам, в которой он сейчас сам себе признался. В эту же минуту он и сам сознавал, что мысли его порою мешаются и что он очень слаб: второй день как уж он почти совсем ничего не ел. 
#         Он был до того худо одет, что иной, даже и привычный человек, посовестился бы днем выходить в таких лохмотьях на улицу. Впрочем, квартал был таков, что костюмом здесь было трудно кого-нибудь удивить. Близость Сенной, обилие известных заведений и, по преимуществу, цеховое и ремесленное население, скученное в этих серединных петербургских улицах и переулках, пестрили иногда общую панораму такими субъектами, что странно было бы и удивляться при встрече с иною фигурой. Но столько злобного презрения уже накопилось в душе молодого человека, что, несмотря на всю свою, иногда очень молодую, щекотливость, он менее всего совестился своих лохмотьев на улице. Другое дело при встрече с иными знакомыми или с прежними товарищами, с которыми вообще он не любил встречаться... А между тем, когда один пьяный, которого неизвестно почему и куда провозили в это время по улице в огромной телеге, запряженной огромною ломовою лошадью, крикнул ему вдруг, проезжая: "Эй ты, немецкий шляпник!" -- и заорал во всё горло, указывая на него рукой, -- молодой человек вдруг остановился и судорожно схватился за свою шляпу. Шляпа эта была высокая, круглая, циммермановская, но вся уже изношенная, совсем рыжая, вся в дырах и пятнах, без полей и самым безобразнейшим углом заломившаяся на сторону. Но не стыд, а совсем другое чувство, похожее даже на испуг, охватило его. 
#         "Я так и знал! -- бормотал он в смущении, -- я так и думал! Это уж всего сквернее! Вот эдакая какая-нибудь глупость, какая-нибудь пошлейшая мелочь, весь замысел может испортить! Да, слишком приметная шляпа... Смешная, потому и приметная... К моим лохмотьям непременно нужна фуражка, хотя бы старый блин какой-нибудь, а не этот урод. Никто таких не носит, за версту заметят, запомнят... главное, потом запомнят, ан и улика. Тут нужно быть как можно неприметнее... Мелочи, мелочи главное!.. Вот эти-то мелочи и губят всегда и всё..." 
#            
#      ';
#      --------------------------------------------------
#      commit;
#      --/*
#      --TEMPLY COMMENTED UNTIL CORE-5221 IS OPEN:
#      set echo on;
#      show collation;
#      show domain;
#      show exception; -- <<<<<<<<<<<<<
#      show sequence;
#      show table;
#      show trigger;
#      show view;
#      show procedure;
#      show role;
#      --*/
#      set list on;
#      set echo off;
#      select 'Metadata created OK.' as msg from rdb$database;
#  	
#  ''' % dict(globals(), **locals())
#  
#  
#  f_checksql = open( os.path.join(context['temp_directory'], 'tmp_0986_w1251.sql'), 'w' )
#  f_checksql.write( non_ascii_ddl.decode('utf8').encode('cp1251') )
#  flush_and_close( f_checksql )
#  
#  # Result: file 'tmp_0986_w1251' is encoded in cp1251 and contains SQL statements to be executed.
#  
#  ###########################################################################################################
#  ###  check-1:  attempt to apply DDL with non-ascii characters __WITHOUT__ charset specifying (for ISQL) ###
#  ###########################################################################################################
#  
#  f_apply_cset_none_log = open( os.path.join(context['temp_directory'],'tmp_0986_apply_cset_none.log'), 'w')
#  f_apply_cset_none_err = open( os.path.join(context['temp_directory'],'tmp_0986_apply_cset_none.err'), 'w')
#  
#  subprocess.call( [ context['isql_path'], "-q", "-i", f_checksql.name ],
#                   stdout = f_apply_cset_none_log,
#                   stderr = f_apply_cset_none_err
#                 )
#  
#  # This file should contain only FIRST statement from DDL hich contains non-ascii characters:
#  # (because of 'set BAIL on' ISQL should immediately terminate its job):
#  # create collation "Циферки" for utf8 from unicode case insensitive 'NUMERIC-SORT=1';:
#  #
#  flush_and_close( f_apply_cset_none_log )
#  
#  # This file should contain error on 1st DDL statement which contains non-ascii characters:
#  # FB 3.x:
#  #     Statement failed, SQLSTATE = 22000
#  #     unsuccessful metadata update
#  #     -CREATE COLLATION Циферки failed
#  #     -Malformed string
#  # FB 4.x:
#  #     Statement failed, SQLSTATE = 22018
#  #     arithmetic exception, numeric overflow, or string truncation
#  #     -Cannot transliterate character between character sets
#  #
#  flush_and_close( f_apply_cset_none_err )
#  
#  #############################################################################################################
#  ###  check-2:  attempt to apply DDL with non-ascii characters ___WITH___ specifying: ISQL ... -ch WIN1251 ###
#  #############################################################################################################
#  
#  f_apply_cset_1251_log = open( os.path.join(context['temp_directory'],'tmp_0986_apply_cset_1251.log'), 'w')
#  f_apply_cset_1251_err = open( os.path.join(context['temp_directory'],'tmp_0986_apply_cset_1251.err'), 'w')
#  
#  subprocess.call( [ context['isql_path'], "-q", "-i", f_checksql.name, "-ch", "win1251" ],
#                   stdout = f_apply_cset_1251_log,
#                   stderr = f_apply_cset_1251_err
#                 )
#  
#  # This file should contain ALL applied statements, plus final message:
#  # MSG                             Metadata created OK.
#  flush_and_close( f_apply_cset_1251_log )
#  
#  # This file should NOT contain any errors:
#  flush_and_close( f_apply_cset_1251_err )
#  
#  # CHECK RESULTS:
#  ################
#                 
#  # This stdout log should contain only ONE statement (create collation <non_ascii_name> ...),
#  # this DDL failed and caused ISQL to immediately terminate:
#  #
#  with open( f_apply_cset_none_log.name, 'r') as f:
#      for line in f:
#          out_txt='STDLOG WHEN CSET=NONE: ';
#          if line.strip():
#              if line.strip().decode("cp1251").encode('utf8').startswith('create collation'):
#                  print( out_txt + "FOUND EXPECTED 'CREATE COLLATION STATEMENT'" )
#              else:
#                  print( out_txt+'SOME OTHER STATEMENT FOUND' )
#  
#  with open( f_apply_cset_none_err.name, 'r') as f:
#      for line in f:
#          out_txt='STDERR WHEN CSET=NONE: ';
#          if 'SQLSTATE =' in line:
#              if 'SQLSTATE = 22000' in line and engine.startswith('3.')                or                'SQLSTATE = 22018' in line and not engine.startswith('3.'):
#                  print( out_txt+'FOUND EXPECTED SQLSTATE IN ERROR MESSAGE' )
#              else:
#                  print( out_txt+'SOME OTHER ERROR FOUND: '+line )
#  
#  # This log should contain 'magic text' which tells that all finished OK:
#  # MSG                             Metadata created OK.
#  
#  if 'Metadata created OK.' in open(f_apply_cset_1251_log.name).read():
#      print('STDLOG WHEN CSET=1251: ALL FINISHED OK.')
#      
#  # This log should be EMPTY: when we used '-ch win1251' then metadata
#  # with non-ascii names in DB objects should be created successfully:
#  #
#  with open( f_apply_cset_1251_err.name, 'r') as f:
#      for line in f:
#          if line:
#              print('Unexpected STDERR when use -ch win1251: ' + line)
#  
#  # CLEANUP
#  #########
#  time.sleep(1)
#  cleanup( ( f_apply_cset_none_log, f_apply_cset_none_err, f_apply_cset_1251_log, f_apply_cset_1251_err,f_checksql, ) )
#  
#    
#---
#act_1 = python_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    STDLOG WHEN CSET=NONE: FOUND EXPECTED 'CREATE COLLATION STATEMENT'
    STDERR WHEN CSET=NONE: FOUND EXPECTED SQLSTATE IN ERROR MESSAGE
    STDLOG WHEN CSET=1251: ALL FINISHED OK.
  """

@pytest.mark.version('>=3.0')
@pytest.mark.xfail
def test_1(db_1):
    pytest.fail("Test not IMPLEMENTED")


