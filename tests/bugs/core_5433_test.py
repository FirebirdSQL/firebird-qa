#coding:utf-8
#
# id:           bugs.core_5433
# title:        Minor performance optimization - avoid additional database attachment from security objects mapping code
# decription:
#                  After discuss with Alex (letters 08-10 mar 2017) it was decided to estimate effect of optimization
#                  by evaluating difference of attachment_id between two subsequent connections to DB.
#                  NB: Alex said that there was no way to see special service attachment because is was made with turned off
#                  ability to trace it (see letter 09-mar-2017 16:16).
#
#                  Checked on:
#                      4.0.0.477, 29-dec-2016: ClassicServer diff=2 - one of these two attachments should be removed
#                      4.0.0.494, 10-jan-2017: ClassicServer diff=1 - Ok, expected.
#                  ::: NB :::
#                  SuperServer will have diff=3 (THREE) attachment_id because of CacheWriter and GarbageCollector.
#                  For that reason we detect FB architecture here and SKIP checking SS results by substitution of
#                  dummy "OK" instead.
#
# tracker_id:   CORE-5433
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  import fdb
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#
#  def get_fb_arch(a_dsn):
#     try:
#        con1 = fdb.connect(dsn = a_dsn)
#        con2 = fdb.connect(dsn = a_dsn)
#
#        cur1 = con1.cursor()
#
#        sql=(
#               "select count(distinct a.mon$server_pid), min(a.mon$remote_protocol), max(iif(a.mon$remote_protocol is null,1,0))"
#              +" from mon$attachments a"
#              +" where a.mon$attachment_id in (%s, %s) or upper(a.mon$user) = upper('%s')"
#              % (con1.attachment_id, con2.attachment_id, 'cache writer')
#            )
#
#        cur1.execute(sql)
#        for r in cur1.fetchall():
#            server_cnt=r[0]
#            server_pro=r[1]
#            cache_wrtr=r[2]
#
#        if server_pro == None:
#            fba='Embedded'
#        elif cache_wrtr == 1:
#            fba='SS'
#        elif server_cnt == 2:
#            fba='CS'
#        else:
#
#            f1=con1.db_info(fdb.isc_info_fetches)
#
#            cur2=con2.cursor()
#            cur2.execute('select 1 from rdb$database')
#            for r in cur2.fetchall():
#               pass
#
#            f2=con1.db_info(fdb.isc_info_fetches)
#
#            fba = 'SC' if f1 ==f2 else 'SS'
#
#        #print(fba, con1.engine_version, con1.version)
#        return fba
#
#     finally:
#        con1.close()
#        con2.close()
#
#  fb_arch= get_fb_arch(dsn)
#
#  if fb_arch=='CS' or fb_arch=='CS':
#      con1=fdb.connect(dsn=dsn)
#      att1=con1.attachment_id
#      con1.close()
#
#      con2=fdb.connect(dsn=dsn)
#      att2=con2.attachment_id
#      con2.close()
#
#      print( 'OK' if att2-att1<=1 else ('BAD: attachment_id diff=%d -- too big.' % (att2-att1) ) )
#
#  else:
#      print('OK')
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    if act_1.get_server_architecture() in ['CS', 'SC']:
        with act_1.db.connect() as con:
            att1 = con.info.id
        with act_1.db.connect() as con:
            att2 = con.info.id
        assert att2 - att1 == 1
