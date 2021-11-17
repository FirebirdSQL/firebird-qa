#coding:utf-8
#
# id:           bugs.core_3231
# title:        OVERLAY() fails when used with text BLOBs containing multi-byte chars
# decription:
# tracker_id:   CORE-3231
# min_versions: ['2.1.5']
# versions:     2.1.5
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 2.1.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# c = db_conn.cursor()
#  try:
#    c.execute("with q(s) as (select cast('abcdefghijklmno' as blob sub_type 1 character set utf8) from rdb$database) select overlay (s placing cast('0123456789' as blob sub_type 1 character set utf8) from 5) from q")
#    c.fetchall()
#  except Exception,e:
#    print ("Test non multi-bytes Failed")
#    print (e)
#  else:
#    pass
#  try:
#    c.execute("with q(s) as (select cast('abcdefghijklmno' as blob sub_type 1 character set utf8) from rdb$database) select overlay (s placing cast(_iso8859_1 'áé' as blob sub_type 1 character set utf8) from 5) from q")
#    c.fetchall()
#  except Exception,e:
#    print ("Test utf8 Failed")
#    print (e)
#  else:
#    pass
#  try:
#    c.execute("with q(s) as (select cast('abcdefghijklmno' as blob sub_type 1 character set utf8) from rdb$database) select overlay (s placing cast(_iso8859_1 'áé' as blob sub_type 1 character set iso8859_1) from 5) from q")
#    c.fetchall()
#  except Exception,e:
#    print ("Test iso8859_1 Failed")
#    print (e)
#  else:
#    pass
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    with act_1.db.connect() as con:
        c = con.cursor()
        # Test non multi-bytes
        c.execute("with q(s) as (select cast('abcdefghijklmno' as blob sub_type 1 character set utf8) from rdb$database) select overlay (s placing cast('0123456789' as blob sub_type 1 character set utf8) from 5) from q")
        # Test UTF8
        c.execute("with q(s) as (select cast('abcdefghijklmno' as blob sub_type 1 character set utf8) from rdb$database) select overlay (s placing cast(_iso8859_1 'áé' as blob sub_type 1 character set utf8) from 5) from q")
        # Test ISO8859_1
        c.execute("with q(s) as (select cast('abcdefghijklmno' as blob sub_type 1 character set utf8) from rdb$database) select overlay (s placing cast(_iso8859_1 'áé' as blob sub_type 1 character set iso8859_1) from 5) from q")
