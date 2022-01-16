#coding:utf-8
#
# id:           bugs.core_4582
# title:        Within linger period one can not change some database properties
# decription:
#                  Confirmed on WI-T3.0.0.31374 Beta 1: running GFIX -buffers N has NO affect if this is done within linger period
#                  Results for 22.05.2017:
#                       fb30Cs, build 3.0.3.32725: OK, 4.703ss.
#                       fb30SC, build 3.0.3.32725: OK, 2.469ss.
#                       FB30SS, build 3.0.3.32725: OK, 1.922ss.
#                       FB40CS, build 4.0.0.645: OK, 5.047ss.
#                       FB40SC, build 4.0.0.645: OK, 2.703ss.
#                       FB40SS, build 4.0.0.645: OK, 2.187ss.
#
# tracker_id:   CORE-4582
# min_versions: ['3.0']
# versions:     3.0
# qmid:

import pytest
from firebird.qa import db_factory, python_act, Action
from firebird.driver import DbWriteMode, DbAccessMode, ShutdownMode, ShutdownMethod, \
     SrvStatFlag

# version: 3.0
# resources: None

substitutions_1 = [('^((?!:::MSG:::|buffers|before|after|Attributes).)*$', ''),
                   ('Page buffers([\t]|[ ])+', 'Page buffers '),
                   ('Attributes([\t]|[ ])+', 'Attributes '), ('N/A', 'YES')]

init_script_1 = """
    -- Result of this test on WI-T3.0.0.31374 Beta 1:
    -- Expected standard output from Python does not match actual output.
    -- - GFIX could change buffers ? =>  YES
    -- ?                                 ^^^
    -- + GFIX could change buffers ? =>  NO!
    -- ?                                 ^^^

    set term ^;
    -- Aux procedure that determines: is current connection to SuperServer ?
    -- If yes, returns current value of page buffers, otherwise (SC/CS) always return -1, in order to
    -- make final output = 'N/A' and give 'substitutions' section handle this case as acceptable.
    create or alter procedure sp_get_buff returns(mon_buffers int) as
    begin
        mon_buffers = -1;
        if (exists(select * from mon$attachments where mon$user containing 'cache writer' and mon$system_flag = 1))
        then
            select mon$page_buffers from mon$database into mon_buffers;

        suspend;

    end
    ^
    set term ;^
    commit;
    recreate table log(buf_before int, buf_after int);
    commit;
"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

# test_script_1
#---
#
#  import os
#  os.environ["ISC_USER"] = user_name
#  os.environ["ISC_PASSWORD"] = user_password
#  db_conn.close()
#
#  script='''
#      insert into log(buf_before) select mon_buffers from sp_get_buff;
#      commit;
#      alter database set linger to 15;
#      commit;
#      set list on;
#      select rdb$linger as ":::MSG::: linger_time" from rdb$database;
#  '''
#
#  print (':::MSG::: Starting ISQL setting new value for linger...')
#  runProgram('isql',[dsn],script)
#  print (':::MSG::: ISQL setting new value for linger finished.')
#
#  print (':::MSG::: Starting GFIX setting new value for page buffers...')
#  runProgram('gfix',[dsn,'-buffers','3791'])
#  runProgram('gfix',[dsn,'-w','async'])
#  runProgram('gfix',[dsn,'-mode','read_only'])
#  runProgram('gfix',[dsn,'-sh','single', '-at', '20'])
#  runProgram('gstat',['-h',dsn])
#  runProgram('gfix',[dsn,'-online'])
#  runProgram('gfix',[dsn,'-mode','read_write'])
#  print (':::MSG::: GFIX setting new value for page buffers finished.')
#  print (':::MSG::: Starting ISQL for extract old and new value of page buffers...')
#  script='''
#      set list on;
#      update log set buf_after = (select mon_buffers from sp_get_buff);
#      commit;
#      select iif( g.buf_before > 0,
#                  iif( g.buf_before is distinct from g.buf_after, 'YES', 'NO!' ),
#                  'N/A'
#                ) as "GFIX could change buffers ? =>"
#      from log g;
#  '''
#  runProgram('isql',[dsn],script)
#  print (':::MSG::: ISQL for extract old and new value of page finished.')
#
#---

act_1 = python_act('db_1', substitutions=substitutions_1)

expected_stdout_1 = """
    :::MSG::: Starting ISQL setting new value for linger...
    :::MSG::: linger_time           15
    :::MSG::: ISQL setting new value for linger finished.
    :::MSG::: Starting GFIX setting new value for page buffers...
    Page buffers 3791
    Attributes single-user maintenance, read only
    :::MSG::: GFIX setting new value for page buffers finished.
    :::MSG::: Starting ISQL for extract old and new value of page buffers...
    GFIX could change buffers ? =>  YES
    :::MSG::: ISQL for extract old and new value of page finished.
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action, capsys):
    # [pcisar] 21.12.2021
    # FAILs on v4.0.0.2496 and v3.0.8.33535 as database couldn't be reverted to online
    # state
    pytest.skip("FIXME")
    script_1 = """
    insert into log(buf_before) select mon_buffers from sp_get_buff;
    commit;
    alter database set linger to 15;
    commit;
    set list on;
    select rdb$linger as ":::MSG::: linger_time" from rdb$database;
"""
    print (':::MSG::: Starting ISQL setting new value for linger...')
    act_1.isql(switches=[], input=script_1)
    print (':::MSG::: ISQL setting new value for linger finished.')
    print (':::MSG::: Starting GFIX setting new value for page buffers...')
    #with act_1.connect_server() as srv:
        #srv.database.set_default_cache_size(database=act_1.db.db_path, size=3791)
        #srv.database.set_write_mode(database=act_1.db.db_path, mode=DbWriteMode.ASYNC)
        #srv.database.set_access_mode(database=act_1.db.db_path, mode=DbAccessMode.READ_ONLY)
        #srv.database.shutdown(database=act_1.db.db_path, mode=ShutdownMode.SINGLE,
                              #method=ShutdownMethod.DENNY_ATTACHMENTS, timeout=20)
        #srv.database.get_statistics(database=act_1.db.db_path, flags=SrvStatFlag.HDR_PAGES,
                                    #callback=print)
        #srv.database.bring_online(database=act_1.db.db_path)
        #srv.database.set_access_mode(database=act_1.db.db_path, mode=DbAccessMode.READ_WRITE)
    act_1.reset()
    act_1.gfix(switches=['-buffers', '3791', act_1.db.dsn])
    act_1.reset()
    act_1.gfix(switches=['-write','async', act_1.db.dsn])
    act_1.reset()
    act_1.gfix(switches=['-mode','read_only', act_1.db.dsn])
    act_1.reset()
    act_1.gfix(switches=['-shutdown','single', '-at', '20', act_1.db.dsn])
    act_1.reset()
    act_1.gstat(switches=['-h'])
    print(act_1.stdout)
    act_1.reset()
    # [pcisar] 21.12.2021
    # FAILs on v4.0.0.2496 and v3.0.8.33535 as database couldn't be reverted to online
    # state
    act_1.gfix(switches=[act_1.db.dsn, '-online'])
    act_1.reset()
    act_1.gfix(switches=['-mode','read_write', act_1.db.dsn])
    print (':::MSG::: GFIX setting new value for page buffers finished.')
    print (':::MSG::: Starting ISQL for extract old and new value of page buffers...')
    script_2 = """
    set list on;
    update log set buf_after = (select mon_buffers from sp_get_buff);
    commit;
    select iif( g.buf_before > 0,
                iif( g.buf_before is distinct from g.buf_after, 'YES', 'NO!' ),
                'N/A'
              ) as "GFIX could change buffers ? =>"
    from log g;
"""
    act_1.reset()
    act_1.isql(switches=[], input=script_2)
    print(act_1.stdout)
    print (':::MSG::: ISQL for extract old and new value of page finished.')
    # Check
    act_1.expected_stdout = expected_stdout_1
    act_1.stdout = capsys.readouterr().out
    assert act_1.clean_stdout == act_1.clean_expected_stdout
