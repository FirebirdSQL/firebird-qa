#coding:utf-8

"""
ID:          issue-5209
ISSUE:       5209
TITLE:       ALTER DOMAIN ... TO <new_name> allows to specify <new_name> matching to 'RDB$[[:DIGIT:]]*'
DESCRIPTION:
JIRA:        CORE-4917
FBTEST:      bugs.core_4917
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    -- CREATION:
    -- #########

    -- First, check that direct creation of domain with 'RDB$' prefix is disabled:
    create domain rdb$1 int;

    -- This also should FAIL becase new domain name is written in UPPER case (despite quotes):
    create domain "RDB$2" int;

    -- This should pass because new though name starts with 'rdb$' it
    -- is written in quotes and not in upper case:
    create domain "rdb$1" int;

    -- ALTERING:
    -- #########

    alter domain "rdb$1" to foo;

    alter domain foo to "rdb$1";

    -- This should pass because new though name starts with 'rdb$' it
    -- is written in quotes and not in upper case:
    alter domain "rdb$1" to "rdb$2";

    -- this should FAIL:
    alter domain "rdb$2" to RDB$3;

    -- this also should FAIL becase new domain name is written in UPPER case (despite quotes):
    alter domain "rdb$2" to "RDB$3";

    show domain;

"""

act = isql_act('db', test_script)

expected_stdout = """
    rdb$2
"""

expected_stderr = """
    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE DOMAIN RDB$1 failed
    -SQL error code = -637
    -Implicit domain name RDB$1 not allowed in user created domain

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -CREATE DOMAIN RDB$2 failed
    -SQL error code = -637
    -Implicit domain name RDB$2 not allowed in user created domain

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER DOMAIN rdb$2 failed
    -SQL error code = -637
    -Implicit domain name RDB$3 not allowed in user created domain

    Statement failed, SQLSTATE = 42000
    unsuccessful metadata update
    -ALTER DOMAIN rdb$2 failed
    -SQL error code = -637
    -Implicit domain name RDB$3 not allowed in user created domain
"""

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.expected_stderr = expected_stderr
    act.execute()
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)

