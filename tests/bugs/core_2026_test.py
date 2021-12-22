#coding:utf-8
#
# id:           bugs.core_2026
# title:        Problem with a read-only marked database
# decription:
#                  Since FB 2.1 engine performs transliteraion of blobs between character sets.
#                  In this case system blob, stored in UNICODE_FSS, transliterated into connection charset.
#                  To do this, temporary blob is created. Engine didn't support temporary blobs creation in
#                  read-only databases since read-only databases was introduced
#
# tracker_id:   CORE-2026
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action
from firebird.driver import DbAccessMode

# version: 2.5
# resources: None

substitutions_1 = [('RDB\\$DEFAULT_SOURCE.*', '')]

init_script_1 = """
    recreate table test(x integer default 0);
    commit;
"""

db_1 = db_factory(charset='ISO8859_1', sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#
#  script='''
#      set list on;
#      set blob all;
#      select mon$read_only from mon$database;
#      set count on;
#      select RDB$FIELD_NAME, rdb$default_source
#      from rdb$relation_fields
#      where rdb$default_source is not null;
#  '''
#  runProgram('isql',[dsn],script)
#  runProgram('gfix',['-mode','read_only',dsn])
#  runProgram('isql',['-ch','iso8859_1',dsn],script)
#
#
#---

test_script_1 = """
set list on;
set blob all;
select mon$read_only from mon$database;
set count on;
select RDB$FIELD_NAME, rdb$default_source from rdb$relation_fields
where rdb$default_source is not null;
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1_a = """
MON$READ_ONLY                   0
RDB$FIELD_NAME                  X
default 0
Records affected: 1
"""

expected_stdout_1_b = """
MON$READ_ONLY                   1
RDB$FIELD_NAME                  X
default 0
Records affected: 1
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1_a
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
    #
    with act_1.connect_server() as srv:
        srv.database.set_access_mode(database=act_1.db.db_path, mode=DbAccessMode.READ_ONLY)
    #
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1_b
    act_1.isql(switches=[], charset='iso8859_1', input=act_1.script)
    assert act_1.clean_stdout == act_1.clean_expected_stdout


