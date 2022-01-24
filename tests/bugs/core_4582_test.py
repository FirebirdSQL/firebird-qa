#coding:utf-8

"""
ID:          issue-4898
ISSUE:       4898
TITLE:       Within linger period one can not change some database properties
DESCRIPTION:
  Confirmed on WI-T3.0.0.31374 Beta 1: running GFIX -buffers N has NO affect if this is done within linger period
NOTES:
[21.12.2021] pcisar
  FAILs on v4.0.0.2496 and v3.0.8.33535 as database couldn't be reverted to online state
JIRA:        CORE-4582
"""

import pytest
from firebird.qa import *
from firebird.driver import DbWriteMode, DbAccessMode, ShutdownMode, ShutdownMethod, \
     SrvStatFlag

substitutions = [('^((?!:::MSG:::|buffers|before|after|Attributes).)*$', ''),
                 ('Page buffers([\t]|[ ])+', 'Page buffers '),
                 ('Attributes([\t]|[ ])+', 'Attributes '), ('N/A', 'YES')]

init_script = """
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

db = db_factory(init=init_script)

act = python_act('db', substitutions=substitutions)

expected_stdout = """
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

@pytest.mark.skip("FIXME: see notes")
@pytest.mark.version('>=3.0')
def test_1(act: Action, capsys):
    script = """
    insert into log(buf_before) select mon_buffers from sp_get_buff;
    commit;
    alter database set linger to 15;
    commit;
    set list on;
    select rdb$linger as ":::MSG::: linger_time" from rdb$database;
    """
    print (':::MSG::: Starting ISQL setting new value for linger...')
    act.isql(switches=[], input=script)
    print (':::MSG::: ISQL setting new value for linger finished.')
    print (':::MSG::: Starting GFIX setting new value for page buffers...')
    #with act.connect_server() as srv:
        #srv.database.set_default_cache_size(database=act.db.db_path, size=3791)
        #srv.database.set_write_mode(database=act.db.db_path, mode=DbWriteMode.ASYNC)
        #srv.database.set_access_mode(database=act.db.db_path, mode=DbAccessMode.READ_ONLY)
        #srv.database.shutdown(database=act.db.db_path, mode=ShutdownMode.SINGLE,
                              #method=ShutdownMethod.DENNY_ATTACHMENTS, timeout=20)
        #srv.database.get_statistics(database=act.db.db_path, flags=SrvStatFlag.HDR_PAGES,
                                    #callback=print)
        #srv.database.bring_online(database=act.db.db_path)
        #srv.database.set_access_mode(database=act.db.db_path, mode=DbAccessMode.READ_WRITE)
    act.reset()
    act.gfix(switches=['-buffers', '3791', act.db.dsn])
    act.reset()
    act.gfix(switches=['-write','async', act.db.dsn])
    act.reset()
    act.gfix(switches=['-mode','read_only', act.db.dsn])
    act.reset()
    act.gfix(switches=['-shutdown','single', '-at', '20', act.db.dsn])
    act.reset()
    act.gstat(switches=['-h'])
    print(act.stdout)
    act.reset()
    # [pcisar] 21.12.2021
    # FAILs on v4.0.0.2496 and v3.0.8.33535 as database couldn't be reverted to online
    # state
    act.gfix(switches=[act.db.dsn, '-online'])
    act.reset()
    act.gfix(switches=['-mode','read_write', act.db.dsn])
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
    act.reset()
    act.isql(switches=[], input=script_2)
    print(act.stdout)
    print (':::MSG::: ISQL for extract old and new value of page finished.')
    # Check
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
