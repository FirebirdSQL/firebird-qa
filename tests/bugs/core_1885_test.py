#coding:utf-8

"""
ID:          issue-897
ISSUE:       897
TITLE:       CREATE COLLATION connection lost under Posix
DESCRIPTION: CREATE COLLATION connection lost under Posix when using LOCALE option
NOTES:
[15.1.2022] pcisar
  For 3.0.7 on Linux this PASS (uses system ICU) but on Windows (includes ICU 52)
  it FAIL unless newer ICU (63) is installed. Hence as this issue was POSIX-only,
  we'll not run it on Windows.
JIRA:        CORE-1885
"""

import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('SPECIFIC_ATTR_BLOB_ID.*', ''),
                 ('COLL-VERSION=\\d{2,}.\\d{2,}', 'COLL-VERSION=111.222'),
                 ('COLL-VERSION=\\d+\\.\\d+\\.\\d+\\.\\d+', 'COLL-VERSION=111.222')]

# version: 3.0

test_script_1 = """
    set list on;
    set count on;
    create collation unicode_enus_ci_4x for utf8 from unicode case insensitive 'LOCALE=en_US';
    commit;

    select
        rc.rdb$collation_name
        ,rc.rdb$collation_attributes
        ,rc.rdb$base_collation_name
        ,rc.rdb$specific_attributes as specific_attr_blob_id
        ,rs.rdb$character_set_name
        --,rs.rdb$number_of_characters
        ,rs.rdb$bytes_per_character
    from rdb$collations rc
    join rdb$character_sets rs
    on rc.rdb$character_set_id = rs.rdb$character_set_id
    where
        rc.rdb$system_flag is distinct from 1
        and rc.rdb$collation_name = upper('unicode_enus_ci_4x');
"""

act_1 = isql_act('db', test_script_1, substitutions=substitutions)

expected_stdout_1 = """
    RDB$COLLATION_NAME              UNICODE_ENUS_CI_4X

    RDB$COLLATION_ATTRIBUTES        3
    RDB$BASE_COLLATION_NAME         UNICODE

    SPECIFIC_ATTR_BLOB_ID           1d:1e7
    COLL-VERSION=153.88;LOCALE=en_US
    RDB$CHARACTER_SET_NAME          UTF8

    RDB$BYTES_PER_CHARACTER         4

    Records affected: 1
"""


@pytest.mark.version('>=3.0,<4.0')
@pytest.mark.platform('Linux', 'Darwin')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

# version: 4.0

test_script_2 = """
    -- ::: NB ::: 31.01.2019
    -- Since builds 4.0.0.1410, 26.01.2019, FULL ICU library icudt63l.dat is included in snapshot,
    -- so this collation *CAN AND MUST* be created w/o errors.

    set list on;
    set count on;
    create collation unicode_enus_ci_4x for utf8 from unicode case insensitive 'LOCALE=en_US';
    commit;

    select
        rc.rdb$collation_name
        ,rc.rdb$collation_attributes
        ,rc.rdb$base_collation_name
        ,rc.rdb$specific_attributes as specific_attr_blob_id
        ,rs.rdb$character_set_name
        --,rs.rdb$number_of_characters
        ,rs.rdb$bytes_per_character
    from rdb$collations rc
    join rdb$character_sets rs
    on rc.rdb$character_set_id = rs.rdb$character_set_id
    where
        rc.rdb$system_flag is distinct from 1
        and rc.rdb$collation_name = upper('unicode_enus_ci_4x');
"""

act_2 = isql_act('db', test_script_2, substitutions=substitutions)

expected_stdout_2 = """
    RDB$COLLATION_NAME              UNICODE_ENUS_CI_4X

    RDB$COLLATION_ATTRIBUTES        3
    RDB$BASE_COLLATION_NAME         UNICODE

    SPECIFIC_ATTR_BLOB_ID           1d:1e7
    COLL-VERSION=153.88;LOCALE=en_US
    RDB$CHARACTER_SET_NAME          UTF8

    RDB$BYTES_PER_CHARACTER         4

    Records affected: 1
"""

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_stdout == act_2.clean_expected_stdout

