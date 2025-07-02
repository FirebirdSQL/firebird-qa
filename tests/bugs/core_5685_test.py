#coding:utf-8

"""
ID:          issue-5951
ISSUE:       5951
TITLE:       Sometime it is impossible to cancel/kill connection executing external query
DESCRIPTION:
  Problem did appear when host "A" established connection to host "B" but could not get completed reply from this "B".
  This can be emulated by following steps:
  1. We establich new remote connection to the same database using EDS mechanism and supply completely new ROLE to force new attachment be created;
  2. Within this EDS we do query to selectable procedure (with name 'sp_unreachable') which surely will not produce any result.
     Bogon IP '192.0.2.2' is used in order to make this SP hang for sufficient time (on Windows it is about 20, on POSIX - about 44 seconds).
  Steps 1 and 2 are implemented by asynchronous call of ISQL: we must have ability to kill its process after.
  When this 'hanging ISQL' is launched, we wait 1..2 seconds and run one more ISQL, which has mission to KILL all attachments except his own.
  This ISQL session is named 'killer', and it writes result of actions to log.
  This "killer-ISQL" does TWO iterations with the same code which looks like 'select ... from mon$attachments' and 'delete from mon$attachments'.
  First iteration must return data of 'hanging ISQL' and also this session must be immediately killed.
  Second iteration must NOT return any data - and this is main check in this test.

  For builds which had bug (before 25.12.2017) one may see that second iteration STILL RETURNS the same data as first one:
  ====
    ITERATION_NO                    1
    HANGING_ATTACH_CONNECTION       1
    HANGING_ATTACH_PROTOCOL         TCP
    HANGING_STATEMENT_STATE         1
    HANGING_STATEMENT_BLOB_ID       0:3
    select * from sp_get_data
    Records affected: 1

    ITERATION_NO                    2
    HANGING_ATTACH_CONNECTION       1
    HANGING_ATTACH_PROTOCOL         TCP
    HANGING_STATEMENT_STATE         1
    HANGING_STATEMENT_BLOB_ID       0:1
    select * from sp_get_data
    Records affected: 1
  ====
  (expected: all fields in ITER #2 must be NULL)
JIRA:        CORE-5685
FBTEST:      bugs.core_5685
NOTES:
    [06.10.2022] pzotov
        Fails on Linux when run in 'batch' mode (i.e. when pytest has to perform the whole tests set).
        Can not reproduce fail when run this test 'separately': it passes, but lasts too longm, ~130 s.
        Test will be re-implemented.
        DEFERRED.
    [09.07.2024] pzotov
        Added item to substitutions related to 'port detached' message that raises in dev build.
        Fixed wrong logic because of missed indentation, see hang_stderr.
    [01.07.2025] pzotov
        Added 'SQL_SCHEMA_PREFIX' and variables - to be substituted in expected_* on FB 6.x
        Separated expected output for FB major versions prior/since 6.x.
        Checked on 6.0.0.876; 5.0.3.1668; 4.0.6.3214; 3.0.13.33813.
"""
import platform
import pytest
import re
import subprocess
import time
from pathlib import Path
from firebird.qa import *
from firebird.driver import ShutdownMode, ShutdownMethod

substitutions = [  ('.*After line.*', '')
                   ,('.*Data source.*', '.*Data source')
                   ,('.*HANGING_STATEMENT_BLOB_ID.*', '')
                   ,('.*-port detached', '')
                ]

init_script = """
    create sequence g;
    commit;
    set term ^;
    create or alter procedure sp_unreachable returns( unreachable_address varchar(50) ) as
    begin
        for
            execute statement ('select mon$remote_address from mon$attachments a where a.mon$attachment_id = current_connection')
                on external '192.0.2.2:' || rdb$get_context('SYSTEM', 'DB_NAME')
                as user 'SYSDBA' password 'masterkey' role left(replace( uuid_to_char(gen_uuid()), '-', ''), 31)
            into unreachable_address
        do
            suspend;
    end
    ^

    create or alter procedure sp_get_data returns( unreachable_address varchar(50) ) as
    begin
        for
            execute statement ('select u.unreachable_address from sp_unreachable as u')
                on external 'localhost:' || rdb$get_context('SYSTEM', 'DB_NAME')
                as user 'SYSDBA' password 'masterkey' role left(replace( uuid_to_char(gen_uuid()), '-', ''), 31)
            into unreachable_address
        do
            suspend;
    end
    ^
    set term ;^
    commit;
"""

db = db_factory(init=init_script)

act = python_act('db', substitutions=substitutions)

kill_script = """
    set list on;
    set blob all;
    select gen_id(g,1) as ITERATION_NO from rdb$database;
    commit;

    select
         sign(a.mon$attachment_id) as hanging_attach_connection
        ,left(a.mon$remote_protocol,3) as hanging_attach_protocol
        ,s.mon$state as hanging_statement_state
        ,s.mon$sql_text as hanging_statement_blob_id
    from rdb$database d
    left join mon$attachments a on a.mon$remote_process containing 'isql'
        -- do NOT use, field not existed in 2.5.x: and a.mon$system_flag is distinct from 1
        and a.mon$attachment_id is distinct from current_connection
    left join mon$statements s on
        a.mon$attachment_id = s.mon$attachment_id
        and s.mon$state = 1 -- 4.0 Classic: 'SELECT RDB$MAP_USING, RDB$MAP_PLUGIN, ... FROM RDB$AUTH_MAPPING', mon$state = 0
    ;

    set count on;
    delete from mon$attachments a
    where
        a.mon$attachment_id <> current_connection
        and a.mon$remote_process containing 'isql'
    ;
    commit;
"""

hang_script = temp_file('hang_script.sql')
hang_stdout = temp_file('hang_script.out')
hang_stderr = temp_file('hang_script.err')

@pytest.mark.skipif(platform.system() != 'Windows', reason='FIXME: see notes')
@pytest.mark.es_eds
@pytest.mark.version('>=3.0.3')
def test_1(act: Action, hang_script: Path, hang_stdout: Path, hang_stderr: Path,
           capsys):
    hang_script.write_text('set list on; set count on; select * from sp_get_data;')
    pattern_for_failed_statement = re.compile('Statement failed, SQLSTATE = (08006|08003)')
    pattern_for_connection_close = re.compile('(Error (reading|writing) data (from|to) the connection)|(connection shutdown)')
    pattern_for_ignored_messages = re.compile('(-send_packet/send)|(-Killed by database administrator.)')
    killer_output = []
    #
    with open(hang_stdout, mode='w') as hang_out, open(hang_stderr, mode='w') as hang_err:
        p_hang_sql = subprocess.Popen([act.vars['isql'], '-i', str(hang_script),
                                       '-user', act.db.user,
                                       '-password', act.db.password, act.db.dsn],
                                       stdout=hang_out, stderr=hang_err)
        try:
            time.sleep(4)
            for i in range(2):
                act.reset()
                act.isql(switches=[], input=kill_script)
                killer_output.append(act.stdout)
        finally:
            p_hang_sql.terminate()
    # Ensure that database is not busy
    with act.connect_server() as srv:
        srv.database.shutdown(database=act.db.db_path, mode=ShutdownMode.FULL,
                              method=ShutdownMethod.FORCED, timeout=0)
        time.sleep(2)
        srv.database.bring_online(database=act.db.db_path)
    #
    output = []
    for line in hang_stdout.read_text().splitlines():
        if line.strip():
            output.append(f'HANGED ATTACH, STDOUT: {line}')
    for line in hang_stderr.read_text().splitlines():
        if line.strip():
            msg = ''
            if pattern_for_ignored_messages.search(line):
                continue
            elif pattern_for_failed_statement.search(line):
                msg = '<found pattern about failed statement>'
            elif pattern_for_connection_close.search(line):
                msg = '<found pattern about closed connection>'
            else:
                msg = line
    
            if msg.strip():
                output.append(f'HANGED ATTACH, STDERR: {msg}')

    for step in killer_output:
        for line in act.clean_string(step).splitlines():
            if line.strip():
                output.append(f"KILLER ATTACH, STDOUT: {' '.join(line.split())}")

    act.reset()

    SQL_SCHEMA_PREFIX = '' if act.is_version('<6') else '"PUBLIC".'
    STORED_PROC_NAME = "'SP_GET_DATA'" if act.is_version('<6') else '"SP_GET_DATA"'
    expected_stdout = f"""
        HANGED ATTACH, STDOUT: Records affected: 0
        HANGED ATTACH, STDERR: Statement failed, SQLSTATE = 42000
        HANGED ATTACH, STDERR: Execute statement error at isc_dsql_fetch :
        HANGED ATTACH, STDERR: <found pattern about closed connection>
        HANGED ATTACH, STDERR: Statement : select u.unreachable_address from sp_unreachable as u
        .*Data source
        HANGED ATTACH, STDERR: -At procedure {SQL_SCHEMA_PREFIX}{STORED_PROC_NAME} line: 3, col: 9
        HANGED ATTACH, STDERR: <found pattern about failed statement>
        HANGED ATTACH, STDERR: <found pattern about closed connection>
        HANGED ATTACH, STDERR: <found pattern about failed statement>
        HANGED ATTACH, STDERR: <found pattern about closed connection>
        KILLER ATTACH, STDOUT: ITERATION_NO 1
        KILLER ATTACH, STDOUT: HANGING_ATTACH_CONNECTION 1
        KILLER ATTACH, STDOUT: HANGING_ATTACH_PROTOCOL TCP
        KILLER ATTACH, STDOUT: HANGING_STATEMENT_STATE 1
        KILLER ATTACH, STDOUT: select * from sp_get_data
        KILLER ATTACH, STDOUT: Records affected: 1
        KILLER ATTACH, STDOUT: ITERATION_NO 2
        KILLER ATTACH, STDOUT: HANGING_ATTACH_CONNECTION <null>
        KILLER ATTACH, STDOUT: HANGING_ATTACH_PROTOCOL <null>
        KILLER ATTACH, STDOUT: HANGING_STATEMENT_STATE <null>
        KILLER ATTACH, STDOUT: Records affected: 0
    """

    act.expected_stdout = expected_stdout
    act.stdout = '\n'.join(output)
    assert act.clean_stdout == act.clean_expected_stdout
