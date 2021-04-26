#coding:utf-8
#
# id:           bugs.core_1095
# title:        Support BETWEEN predicate for select expressions
# decription:   
#                  Checked on WI-V3.0.2.32670, WI-T4.0.0.503 - all fine.
#                  NOTE. Plan with table name (instead of alias 'R_CHK') in 2nd line was:
#                  ===
#                    PLAN (R_CHK NATURAL)
#                    PLAN (RDB$DATABASE NATURAL) <<<< ??
#                    PLAN (R_OUT NATURAL)
#                  ===
#                  Fixed 28.01.2017 11:51 ("Preserve the alias after the relation/procedure node copying").
#                  https://github.com/FirebirdSQL/firebird/commit/36b86a02e5df20d82855fe1af00bac27022bbf8e
#                  https://github.com/FirebirdSQL/firebird/commit/cbe9ac071f187e7766c2a67fdf47683604361059
#                  Checked on WI-V3.0.2.32677, WI-T4.0.0.519
#                  Checked again 22.11.2017:
#                     3.0.3.32837: OK, 2.781s.
#                     3.0.3.32838: OK, 1.438s.
#                     4.0.0.800: OK, 2.547s.
#                     4.0.0.801: OK, 1.640s.
#                
# tracker_id:   CORE-1095
# min_versions: ['3.0.2']
# versions:     3.0.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.2
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set sqlda_display on;
    set planonly;
    -- Before 3.0.2 following statement failed with:
    -- Statement failed, SQLSTATE = HY004
    -- Unsupported field type specified in BETWEEN predicate.
    select 3 from rdb$database r_out where ((select count(*) from rdb$database r_chk) between ? and ?);

    ----------------------------------------------------------

    -- Following sample is from CORE-5596 (added 22.11.2017).
    -- On 2.5.x it issues:
    --   Statement failed, SQLSTATE = XX000
    --   internal Firebird consistency check ((CMP) copy: cannot remap (221), file: cmp.cpp line: 3091)
    select 1
    from rdb$database
    where
        iif(
             exists( select 1 from rdb$database )
           , 0e0
           , 0e0
           )
        between ? and ?
    ;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    INPUT message field count: 2
    01: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
      :  name:   alias:
      : table:   owner:
    02: sqltype: 580 INT64 Nullable scale: 0 subtype: 0 len: 8
      :  name:   alias:
      : table:   owner:

    PLAN (R_CHK NATURAL)
    PLAN (R_CHK NATURAL)
    PLAN (R_OUT NATURAL)

    OUTPUT message field count: 1
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
      :  name: CONSTANT  alias: CONSTANT
      : table:   owner:



    INPUT message field count: 2
    01: sqltype: 480 DOUBLE scale: 0 subtype: 0 len: 8
      :  name:   alias:
      : table:   owner:
    02: sqltype: 480 DOUBLE scale: 0 subtype: 0 len: 8
      :  name:   alias:
      : table:   owner:

    PLAN (RDB$DATABASE NATURAL)
    PLAN (RDB$DATABASE NATURAL)
    PLAN (RDB$DATABASE NATURAL)

    OUTPUT message field count: 1
    01: sqltype: 496 LONG scale: 0 subtype: 0 len: 4
      :  name: CONSTANT  alias: CONSTANT
      : table:   owner:

  """

@pytest.mark.version('>=3.0.2')
def test_core_1095_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

