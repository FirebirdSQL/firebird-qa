#coding:utf-8
#
# id:           bugs.core_5271
# title:        Regression: Can not create large index
# decription:
#                   Confirmed bug on WI-T4.0.0.246 (checked SS, SC), get in STDERR:
#                   ===
#                       Statement failed, SQLSTATE = HY000
#                       sort error
#                       -No free space found in temporary directories
#                       -operating system directive CreateFile failed
#                       -    ,
#                   ===
#                   TempCacheLimit = default, database grows up to 83M (for SS).
#                   All works fine on WI-T4.0.0.254.
#
# tracker_id:   CORE-5271
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, python_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=16384, sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#  sql_ddl='''
#      recreate table t1(
#        s varchar(4000) not null
#      );
#
#      commit;
#      set term !;
#
#      execute block
#      as
#        declare i int = 0;
#      begin
#        -- min = 7275 when database page_size=32768 and index key length = 8000
#        -- min= 14750 when database page_size=16384 and index key length = 4000
#        -- min= 29000 when database page_size=16384 and index key length = 2000
#        while (i < 14750) do
#        begin
#          insert into t1(s) values( rpad('', 4000, uuid_to_char( gen_uuid() ) )  );
#          i = i + 1;
#        end
#      end!
#
#      set term ;!
#
#      commit;
#      alter table t1 add constraint pk_t1 primary key (s) using index pk_t1_s;
#      commit;
#
#      set list on;
#      set count on;
#      select rdb$index_name, rdb$relation_name, rdb$unique_flag,rdb$segment_count
#      from rdb$indices
#      where rdb$index_name = upper('pk_t1_s');
#  '''
#  runProgram('gfix',[dsn, '-w', 'async'])
#  runProgram('isql',[dsn], sql_ddl)
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    RDB$INDEX_NAME                  PK_T1_S
    RDB$RELATION_NAME               T1
    RDB$UNIQUE_FLAG                 1
    RDB$SEGMENT_COUNT               1
    Records affected: 1
"""

test_sript_1 = """
    recreate table t1(
      s varchar(4000) not null
    );

    commit;
    set term !;

    execute block
    as
      declare i int = 0;
    begin
      -- min = 7275 when database page_size=32768 and index key length = 8000
      -- min= 14750 when database page_size=16384 and index key length = 4000
      -- min= 29000 when database page_size=16384 and index key length = 2000
      while (i < 14750) do
      begin
        insert into t1(s) values( rpad('', 4000, uuid_to_char( gen_uuid() ) )  );
        i = i + 1;
      end
    end!

    set term ;!

    commit;
    alter table t1 add constraint pk_t1 primary key (s) using index pk_t1_s;
    commit;

    set list on;
    set count on;
    select rdb$index_name, rdb$relation_name, rdb$unique_flag,rdb$segment_count
    from rdb$indices
    where rdb$index_name = upper('pk_t1_s');
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.db.set_async_write()
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=[], input=test_sript_1)
    assert act_1.clean_stdout == act_1.clean_expected_stdout


