#coding:utf-8
#
# id:           bugs.core_1885
# title:        CREATE COLLATION connection lost under Posix
# decription:   CREATE COLLATION connection lost under Posix when using LOCALE option
# tracker_id:   CORE-1885
# min_versions: []
# versions:     3.0, 4.0
# qmid:         bugs.core_1885-250

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    -- Attribute 'LOCALE=en_US' is defined for charset = ISO8859_1 rather that for UTF8, see intl/fbintl.conf
    CREATE COLLATION UNICODE_ENUS_CI_3X FOR UTF8 FROM UNICODE CASE INSENSITIVE 'LOCALE=en_US';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    unsuccessful metadata update
    -CREATE COLLATION UNICODE_ENUS_CI_3X failed
    -Invalid collation attributes
  """

@pytest.mark.version('>=3.0,<4.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

# version: 4.0
# resources: None

substitutions_2 = [('SPECIFIC_ATTR_BLOB_ID.*', ''), ('COLL-VERSION=\\d+\\.\\d+\\.\\d+\\.\\d+', 'COLL-VERSION=xx'), ('COLL-VERSION=\\d+\\.\\d+', 'COLL-VERSION=xx')]

init_script_2 = """"""

db_2 = db_factory(sql_dialect=3, init=init_script_2)

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

act_2 = isql_act('db_2', test_script_2, substitutions=substitutions_2)

expected_stdout_2 = """
    RDB$COLLATION_NAME              UNICODE_ENUS_CI_4X

    RDB$COLLATION_ATTRIBUTES        3
    RDB$BASE_COLLATION_NAME         UNICODE

    SPECIFIC_ATTR_BLOB_ID           1d:1e7
    COLL-VERSION=xx;LOCALE=en_US
    RDB$CHARACTER_SET_NAME          UTF8

    RDB$BYTES_PER_CHARACTER         4

    Records affected: 1
  """

@pytest.mark.version('>=4.0')
def test_2(act_2: Action):
    act_2.expected_stdout = expected_stdout_2
    act_2.execute()
    assert act_2.clean_expected_stdout == act_2.clean_stdout

