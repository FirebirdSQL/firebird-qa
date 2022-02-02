#coding:utf-8

"""
ID:          issue-5508
ISSUE:       5508
TITLE:       Allow to enforce IPv4 or IPv6 in URL-like connection strings
DESCRIPTION:
JIRA:        CORE-5229
FBTEST:      bugs.core_5229
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

expected_stdout = """
    PROCOTOL_WHEN_CONNECT_FROM_OS   TCPv4
    PROCOTOL_WHEN_CONNECT_FROM_ISQL TCPv4
    PROTOCOL_WHEN_CONNECT_BY_ES_EDS TCPv4
    PROCOTOL_WHEN_CONNECT_FROM_ISQL TCPv6
    PROTOCOL_WHEN_CONNECT_BY_ES_EDS TCPv6
"""

@pytest.mark.version('>=3.0.1')
def test_1(act: Action):
    sql_chk = f"""
        set list on;
        select mon$remote_protocol as procotol_when_connect_from_os
        from mon$attachments where mon$attachment_id = current_connection;

        commit;
        connect 'inet4://{act.db.db_path}';

        select mon$remote_protocol as procotol_when_connect_from_isql
        from mon$attachments where mon$attachment_id = current_connection;

        set term ^;
        execute block returns(protocol_when_connect_by_es_eds varchar(20) ) as
            declare stt varchar(255) = 'select mon$remote_protocol from mon$attachments where mon$attachment_id = current_connection';
        begin
            for
                execute statement (stt)
                    on external 'inet4://{act.db.db_path}'
                    as user '{act.db.user}' password '{act.db.password}'
                into protocol_when_connect_by_es_eds
            do
                suspend;
        end
        ^
        set term ;^
        commit;

        -- since 27.10.2019:
        connect 'inet6://{act.db.db_path}';

        select mon$remote_protocol as procotol_when_connect_from_isql
        from mon$attachments where mon$attachment_id = current_connection;

        set term ^;
        execute block returns(protocol_when_connect_by_es_eds varchar(20) ) as
            declare stt varchar(255) = 'select mon$remote_protocol from mon$attachments where mon$attachment_id = current_connection';
        begin
            for
                execute statement (stt)
                    on external 'inet6://{act.db.db_path}'
                    as user '{act.db.user}' password '{act.db.password}'
                into protocol_when_connect_by_es_eds
            do
                suspend;
        end
        ^
        set term ;^
        commit;

        --                                    ||||||||||||||||||||||||||||
        -- ###################################|||  FB 4.0+, SS and SC  |||##############################
        --                                    ||||||||||||||||||||||||||||
        -- If we check SS or SC and ExtConnPoolLifeTime > 0 (config parameter FB 4.0+) then current
        -- DB (bugs.core_NNNN.fdb) will be 'captured' by firebird.exe process and fbt_run utility
        -- will not able to drop this database at the final point of test.
        -- Moreover, DB file will be hold until all activity in firebird.exe completed and AFTER this
        -- we have to wait for <ExtConnPoolLifeTime> seconds after it (discussion and small test see
        -- in the letter to hvlad and dimitr 13.10.2019 11:10).
        -- This means that one need to kill all connections to prevent from exception on cleanup phase:
        -- SQLCODE: -901 / lock time-out on wait transaction / object <this_test_DB> is in use
        -- #############################################################################################
        delete from mon$attachments where mon$attachment_id != current_connection;
        commit;
        """
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q', f'inet4://{act.db.db_path}'], input=sql_chk, connect_db=False)
    assert act.clean_stdout == act.clean_expected_stdout

