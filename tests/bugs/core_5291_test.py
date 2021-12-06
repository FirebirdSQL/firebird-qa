#coding:utf-8
#
# id:           bugs.core_5291
# title:        Error messages differ when regular user tries to RESTORE database, depending on his default role and (perhaps) system privilege USE_GBAK_UTILITY
# decription:
#                  Works fine on 4.0.0.316.
#
# tracker_id:   CORE-5291
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from pathlib import Path
from firebird.qa import db_factory, python_act, Action, user_factory, User, temp_file

# version: 4.0
# resources: None

substitutions_1 = [('gbak: ERROR:no permission for CREATE access to DATABASE.*',
                    'gbak: ERROR:no permission for CREATE access to DATABASE'),
                   ('gbak: ERROR:    failed to create database.*',
                    'gbak: ERROR:    failed to create database'),
                   ('gbak: ERROR:failed to create database localhost:.*',
                    'gbak: ERROR:failed to create database localhost')]

init_script_1 = """
    -- This is not needed anymore for new test implementation
    --
    -- set wng off;
    -- create or alter user tmp$c5291_1 password '123' revoke admin role;
    -- create or alter user tmp$c5291_2 password '456' revoke admin role;
    -- commit;
    -- revoke all on all from tmp$c5291_1;
    -- revoke all on all from tmp$c5291_2;
    -- commit;
    -- create role role_for_use_gbak_utility set system privileges to USE_GBAK_UTILITY, SELECT_ANY_OBJECT_IN_DATABASE;
    -- commit;
    -- grant default role_for_use_gbak_utility to user tmp$c5291_2;
    -- commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#  tmpfbk=os.path.join(context['temp_directory'],'tmp_core_5291.fbk')
#  tmpres1=os.path.join(context['temp_directory'],'tmp_core_5291_1.tmp')
#  tmpres2=os.path.join(context['temp_directory'],'tmp_core_5291_2.tmp')
#
#  runProgram('gbak',['-b', dsn, tmpfbk])
#
#  runProgram('gbak',['-se', 'localhost:service_mgr', '-rep', tmpfbk, tmpres1, '-user', 'tmp$c5291_1', '-pas', '123'])
#  runProgram('gbak',['-rep', tmpfbk, 'localhost:' + tmpres2, '-user', 'tmp$c5291_1', '-pas', '123'])
#
#  runProgram('gbak',['-se', 'localhost:service_mgr', '-rep', tmpfbk, tmpres1, '-user', 'tmp$c5291_2', '-pas', '456'])
#  runProgram('gbak',['-rep', tmpfbk, 'localhost:' + tmpres2, '-user', 'tmp$c5291_2', '-pas', '456'])
#
#  runProgram('isql',[dsn],'drop user tmp$c5291_1; drop user tmp$c5291_2;')
#
#  f_list=[tmpfbk, tmpres1, tmpres2]
#
#  for i in range(len(f_list)):
#     if os.path.isfile(f_list[i]):
#         os.remove(f_list[i])
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

user_1 = user_factory(name='tmp$c5291_1', password='123')
user_2 = user_factory(name='tmp$c5291_2', password='456')
fbk_file = temp_file('tmp_core_5291.fbk')
fdb_file_1 = temp_file('tmp_core_5291_1.fdb')
fdb_file_2 = temp_file('tmp_core_5291_2.fdb')

expected_stderr_1 = """
    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:    failed to create database
    gbak: ERROR:    Exiting before completion due to errors
    gbak:Exiting before completion due to errors

    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:failed to create database localhost
    gbak:Exiting before completion due to errors

    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:    failed to create database
    gbak: ERROR:    Exiting before completion due to errors
    gbak:Exiting before completion due to errors

    gbak: ERROR:no permission for CREATE access to DATABASE
    gbak: ERROR:failed to create database localhost
    gbak:Exiting before completion due to errors
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action, user_1: User, user_2: User, fbk_file: Path, fdb_file_1: Path,
           fdb_file_2: Path, capsys):
    with act_1.test_role('role_for_use_gbak_utility'):
        with act_1.db.connect() as con:
            con.execute_immediate('alter role role_for_use_gbak_utility set system privileges to USE_GBAK_UTILITY, SELECT_ANY_OBJECT_IN_DATABASE')
            con.commit()
            con.execute_immediate('grant default role_for_use_gbak_utility to user tmp$c5291_2')
            con.commit()
        #
        act_1.gbak(switches=['-b', act_1.db.dsn, str(fbk_file)])
        # User 1
        act_1.reset()
        act_1.expected_stderr = "We expect errors"
        act_1.gbak(switches=['-se', 'localhost:service_mgr', '-rep', str(fbk_file),
                             str(fdb_file_1), '-user', user_1.name, '-pas', user_1.password],
                   credentials=False)
        print(act_1.stderr)
        # User 1
        act_1.reset()
        act_1.expected_stderr = "We expect errors"
        act_1.gbak(switches=['-rep', str(fbk_file), f'localhost:{fdb_file_2}',
                             '-user', user_1.name, '-pas', user_1.password], credentials=False)
        print(act_1.stderr)
        # User 2
        act_1.reset()
        act_1.expected_stderr = "We expect errors"
        act_1.gbak(switches=['-se', 'localhost:service_mgr', '-rep', str(fbk_file),
                             str(fdb_file_1), '-user', user_2.name, '-pas', user_2.password],
                   credentials=False)
        print(act_1.stderr)
        # User 2
        act_1.reset()
        act_1.expected_stderr = "We expect errors"
        act_1.gbak(switches=['-rep', str(fbk_file), f'localhost:{fdb_file_2}',
                             '-user', user_2.name, '-pas', user_2.password], credentials=False)
        print(act_1.stderr)
        #
        act_1.reset()
        act_1.expected_stderr = expected_stderr_1
        act_1.stderr = capsys.readouterr().out
        assert act_1.clean_stderr == act_1.clean_expected_stderr
