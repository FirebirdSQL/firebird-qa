#coding:utf-8
#
# id:           bugs.core_4880
# title:        Increase speed of creating package when number of its functions more than several hundreds
# decription:
#                   This test uses TWO auto-generated scripts, both of them have been packed due to their size in files/core_4880.zip
#                   and are unpacked at runtime here.
#                   First script, 'core_4880_fnc.tmp', creates 5'000  STANDALONE functions and adds into log timestamps of start and finish.
#                   Second script, 'core_4880_pkg.tmp', creates PACKAGE with head and body also of 5'000 functions and also adds into log
#                   timestamps for start of 'create package' and finish of 'create package BODY' statements.
#                   Both scripts use simplest body of functions.
#
#                   After both scripts will be finishec, number of seconds is compared for creation:
#                   1) standalone functions and 2) package header and body with the same number of functions.
#                   Then, we evaluate maxValue and minValue in this pair and result of division: maxValue / minValue, casted to num(12,2).
#
#                   Numerous runs showed that this ratio (N) is about 1.2 ... 1.5, and it never was more than 1.8.
#                   It was decided to use N = 2 as max acceptable ratio between time for creation of package and for standalone funcions.
#                   If any kind of objects (package or s/alone funcs) will be created more than N times than another, expected_stdout
#                   will contain phrase about regression.
#
#                   Checked on WI-V3.0.0.32008, machine: P-IV 3.0 Ghz RAM 2Gb, OS = Win XP.
#                   Duration of test on that machine is about 45-55 seconds.
#
#                   13.04.2021. Adapted for run both on Windows and Linux. Checked on:
#                     Windows: 3.0.8.33445, 4.0.0.2416
#                     Linux:   3.0.8.33426, 4.0.0.2416
#
# tracker_id:   CORE-4880
# min_versions: ['3.0']
# versions:     3.0
# qmid:

import pytest
from zipfile import Path
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DbWriteMode

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table log(
         standalone_func_beg timestamp default null,
         standalone_func_end timestamp default null,
         pkg_head_n_body_beg timestamp default null,
         pkg_head_n_body_end timestamp default null
    );
    commit;
    insert into log default values;
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
# import os
#  import zipfile
#
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#
#  db_conn.close()
#  runProgram('gfix',['-w','async',dsn])
#
#  zf = zipfile.ZipFile( os.path.join(context['files_location'],'core_4880.zip') )
#  zf.extractall( context['temp_directory'] )
#  zf.close()
#  runProgram('isql',[dsn,'-q','-i', os.path.join(context['temp_directory'],'core_4880_fnc.tmp') ])
#  runProgram('isql',[dsn,'-q','-i', os.path.join(context['temp_directory'],'core_4880_pkg.tmp') ])
#
#  os.remove( os.path.join(context['temp_directory'],'core_4880_fnc.tmp') )
#  os.remove( os.path.join(context['temp_directory'],'core_4880_pkg.tmp') )
#
#  script="""set list on;
#  set term ^;
#  execute block as
#  begin
#    rdb$set_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO', '2');
#    --                                                       ^
#    --                                               #################
#    --                                               T H R E S H O L D
#    --                                               #################
#  end
#  ^
#  set term ;^
#
#  select iif( x.ratio < cast( rdb$get_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO') as int ),
#              'Ratio is acceptable',
#              'Regression, ratio >= ' || rdb$get_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO') || 'x'
#            ) as result_msg
#        --, x.*
#    from (
#    select
#      standalone_func_sec
#      ,pkg_head_n_body_sec
#      ,cast( iif( pkg_head_n_body_sec > standalone_func_sec, 1.00 * pkg_head_n_body_sec / standalone_func_sec, 1.00 * standalone_func_sec / pkg_head_n_body_sec ) as numeric(12,2) ) as ratio
#      ,cast( 1.00 * pkg_head_n_body_sec / standalone_func_sec as numeric(12,2) ) package_vs_standalone
#      ,cast( 1.00 * standalone_func_sec / pkg_head_n_body_sec as numeric(12,2) ) standalone_vs_package
#    from (
#      select
#         nullif( datediff(second from standalone_func_beg to standalone_func_end), 0) standalone_func_sec
#        ,nullif( datediff(second from pkg_head_n_body_beg to pkg_head_n_body_end), 0) pkg_head_n_body_sec
#      from log
#    )
#  ) x;
#  """
#  runProgram('isql',[dsn,'-q'],script)
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT_MSG                      Ratio is acceptable
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    with act_1.connect_server() as srv:
        srv.database.set_write_mode(database=act_1.db.db_path, mode=DbWriteMode.ASYNC)
    # Read FNC scripts from zip file and execute it
    script_file = Path(act_1.vars['files'] / 'core_4880.zip',
                    at='core_4880_fnc.tmp')
    act_1.script = script_file.read_text()
    act_1.execute()
    # Read PKG scripts from zip file and execute it
    script_file = Path(act_1.vars['files'] / 'core_4880.zip',
                    at='core_4880_pkg.tmp')
    act_1.script = script_file.read_text()
    act_1.execute()
    # Check
    test_script = """
    set list on;
    set term ^;
    execute block as
    begin
      rdb$set_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO', '2');
      --                                                       ^
      --                                               #################
      --                                               T H R E S H O L D
      --                                               #################
    end
    ^
    set term ;^

    select iif(x.ratio < cast( rdb$get_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO') as int ),
               'Ratio is acceptable',
               'Regression, ratio >= ' || rdb$get_context('USER_SESSION', 'MAX_ACCEPTABLE_RATIO') || 'x'
              ) as result_msg
          --, x.*
      from (
      select
        standalone_func_sec,
        pkg_head_n_body_sec,
        cast(iif( pkg_head_n_body_sec > standalone_func_sec, 1.00 * pkg_head_n_body_sec / standalone_func_sec, 1.00 * standalone_func_sec / pkg_head_n_body_sec ) as numeric(12,2) ) as ratio,
        cast(1.00 * pkg_head_n_body_sec / standalone_func_sec as numeric(12,2)) package_vs_standalone,
        cast(1.00 * standalone_func_sec / pkg_head_n_body_sec as numeric(12,2)) standalone_vs_package
      from (
        select
           nullif(datediff(second from standalone_func_beg to standalone_func_end), 0) standalone_func_sec,
           nullif(datediff(second from pkg_head_n_body_beg to pkg_head_n_body_end), 0) pkg_head_n_body_sec
        from log
      )
    ) x;
    """
    act_1.reset()
    act_1.expected_stdout = expected_stdout_1
    act_1.isql(switches=['-q'], input=test_script)
    assert act_1.clean_stdout == act_1.clean_expected_stdout
