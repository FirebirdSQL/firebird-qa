#coding:utf-8
#
# id:           bugs.core_4715
# title:        Restore of shadowed database fails using -k ("restore without shadow") switch
# decription:   [pcisar] 23.11.2021
#               For unknow reason, on v4.0.0.2496 the gstat -h does not report active shadow
#               and test thus fail.
# tracker_id:   CORE-4715
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, temp_file

# version: 3.0
# resources: None

substitutions_1 = [('^((?!HASH_IN_SOURCE|RDB\\$SHADOW_NUMBER|HASH_IN_RESTORED).)*$', ''),
                   ('.*Shadow 1:.*', 'Shadow present')]

init_script_1 = """
    -- Confirmed on WI-T3.0.0.31374:
    -- command "gbak -rep -k c4715.fbk -user SYSDBA -pas masterke localhost/3000:<path>\\c4715-new.FDB"
    -- produces:
    -- gbak: ERROR:DELETE operation is not allowed for system table RDB$FILES
    -- gbak:Exiting before completion due to errors
    recreate table test(s varchar(30));
    commit;
"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#
#  shd=os.path.join(context['temp_directory'],'core_4715.shd')
#  script = '''create shadow 1 '%s'; commit; insert into test select 'line #'||lpad(row_number()over(), 3, '0') from rdb$types rows 200; commit; set list on; select hash(list(s)) hash_in_source from test; select * from rdb$files;''' % shd
#  runProgram('isql',[dsn,'-q','-user',user_name,'-password',user_password],script)
#  runProgram('gstat',[shd,'-h','-user',user_name,'-password',user_password])
#  fbk = os.path.join(context['temp_directory'],'core_4715-shadowed.fbk')
#  fbn = os.path.join(context['temp_directory'],'core_4715-restored.fdb')
#  runProgram('gbak',['-b','-user',user_name,'-password',user_password,dsn,fbk])
#  runProgram('gbak',['-rep','-k','-user',user_name,'-password',user_password,fbk,fbn])
#  script = '''set list on; select hash(list(s)) hash_in_restored from test;'''
#  runProgram('isql',[fbn,'-q','-user',user_name,'-password',user_password],script)
#  if os.path.isfile(fbk):
#      os.remove(fbk)
#  if os.path.isfile(fbn):
#      os.remove(fbn)
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
HASH_IN_SOURCE                  1499836372373901520
RDB$SHADOW_NUMBER               1
Shadow present
HASH_IN_RESTORED                1499836372373901520
"""

fbk_1 = temp_file('core_4715-shadowed.fbk')
fbn_1 = temp_file('core_4715-restored.fdb')

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, fbk_1: Path, fbn_1: Path, capsys):
    act_1.isql(switches=['-q'],
               input=f'''create shadow 1 '{act_1.db.db_path.with_suffix('.shd')}'; commit; insert into test select 'line #'||lpad(row_number()over(), 3, '0') from rdb$types rows 200; commit; set list on; select hash(list(s)) hash_in_source from test; select * from rdb$files;''')
    print(act_1.stdout)
    act_1.reset()
    act_1.isql(switches=[], input='show database;')
    print(act_1.stdout)
    act_1.reset()
    act_1.gbak(switches=['-b', act_1.db.dsn, str(fbk_1)])
    act_1.reset()
    act_1.gbak(switches=['-rep', '-k', str(fbk_1), str(fbn_1)])
    act_1.reset()
    act_1.isql(switches=['-q', str(fbn_1)], connect_db=False,
               input='set list on; select hash(list(s)) hash_in_restored from test;')
    print(act_1.stdout)
    #
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
