#coding:utf-8
#
# id:           bugs.core_6227
# title:        isc_info_svc_user_dbpath always returns alias of main security database
# decription:
#                   String returned by sevrice manager for 'info_user_dbpath' query must contain PATH + file/alias
#                   rather than only file name or alias of security.db.
#                   If we call os.path.split() then this string will be splitted onto PATH and ALIAS.
#                   The first token (PATH) must contain at least one character if we try to split it using os.sep delimiter.
#                   We check that length of this path is more than zero.
#                   Note that befor fix reply was: ('', security.db') - so the PATH was empty string rather that None!
#
#                   Checked on:
#                       4.0.0.1726 SS: 1.849s.
#                       3.0.5.33232 SS: 0.704s.
#
# tracker_id:   CORE-6227
# min_versions: ['3.0.5']
# versions:     3.0.5
# qmid:         None

import pytest
import os
from firebird.qa import db_factory, python_act, Action

# version: 3.0.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  from fdb import services
#
#  svc = services.connect(host='localhost', user= user_name, password= user_password)
#  security_db_info = svc.get_security_database_path()
#  svc.close()
#
#  print( 'Is DIRECTORY included into security DB info ? => ', ( 'YES' if os.path.split(security_db_info)[0] else ('NO. >' + security_db_info + '<' ) )  )
#
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

@pytest.mark.version('>=3.0.5')
def test_1(act_1: Action):
    with act_1.connect_server() as srv:
        assert os.path.split(srv.info.security_database)[0]
