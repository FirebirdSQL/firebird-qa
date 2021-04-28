#coding:utf-8
#
# id:           bugs.core_2780
# title:        Include client library version and protocol version in mon$attachments
# decription:   
# tracker_id:   CORE-2780
# min_versions: ['3.0']
# versions:     3.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    -- See letter from dimitr, 10-apr-2015 09:19
    select
        -- All platform protovol name: starts with 'TCP'
        iif( cast(mon$remote_protocol as varchar(10) character set utf8) collate unicode_ci starting with 'tcp', 1, 0) is_protocol_valid
        -- Prefixes for client version:
        -- Windows: WI
        -- Linux:   LI
        -- MacOS:   UI (intel) or UP (powerpc)
        -- Solaris: SI (intel) or SO (spark)
        -- HP-UX:   HP
        -- '-T' = Testing; '-V' = RC or release
        -- Sufixes: 'Firebird' followed by space and at least one digit.
        ,iif( cast(mon$client_version as varchar(255) character set utf8) collate unicode_ci
              similar to
              '(WI|LI|UI|UP|SI|SO|HU)[-](T|V){0,1}[0-9]+.[0-9]+.[0-9]+((.?[0-9]+)*)[[:WHITESPACE:]]+firebird[[:WHITESPACE:]]+[0-9]+((.?[0-9]+)*)%', 1, 0) is_client_version_valid
    from mon$attachments
    where mon$attachment_id = current_connection;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    IS_PROTOCOL_VALID               1
    IS_CLIENT_VERSION_VALID         1
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

