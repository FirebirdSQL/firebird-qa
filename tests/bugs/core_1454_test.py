#coding:utf-8
#
# id:           bugs.core_1454
# title:        ALTER mechanism for computed fields
# decription:   Computed field had a lot of inconsistencies and problems
#               It's possible to use a explicit type, but only together with a (new) computed expression.
#               cf core-0847
# tracker_id:   CORE-1454
# min_versions: ['2.5']
# versions:     2.5.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.0
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table t (
      f1 varchar(10),
      f2 varchar(10),
      cf computed by (f1 || ' - ' || f2)
    );

    insert into t (f1,f2) values ('0123456789','abcdefghij');
    commit;
  """

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set width fld_name 31;
    set width fld_expr 80;

    select f1,f2,cf from t;

    select b.rdb$field_name fld_name, cast(a.rdb$computed_source as varchar(80)) fld_expr, a.rdb$field_length fld_length
    from rdb$fields a
    join rdb$relation_fields b
        on a.rdb$field_name = b.rdb$field_source
    where b.rdb$field_name = upper('cf');

    alter table t alter cf type varchar(30) computed by (f1 || ' - ' || f2 || ' - more');
    commit;

    select f1,f2,cf from t;

    select b.rdb$field_name fld_name, cast(a.rdb$computed_source as varchar(80)) fld_expr, a.rdb$field_length fld_length
    from rdb$fields a
    join rdb$relation_fields b
        on a.rdb$field_name = b.rdb$field_source
    where b.rdb$field_name = upper('cf');
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F1                              0123456789
    F2                              abcdefghij
    CF                              0123456789 - abcdefghij
    FLD_NAME                        CF
    FLD_EXPR                        (f1 || ' - ' || f2)
    FLD_LENGTH                      23
    F1                              0123456789
    F2                              abcdefghij
    CF                              0123456789 - abcdefghij - more
    F1                              0123456789
    F2                              abcdefghij
    CF                              0123456789 - abcdefghij - more
    FLD_NAME                        CF
    FLD_EXPR                        (f1 || ' - ' || f2 || ' - more')
    FLD_LENGTH                      30
"""

@pytest.mark.version('>=2.5.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout
