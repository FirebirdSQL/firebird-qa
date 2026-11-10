#coding:utf-8

"""
ID:          functional.tabloid.test_e0d62fab
ISSUE:       https://github.com/FirebirdSQL/firebird/commit/a5ec02b568902e284f1305fe8aaf8f607bed9c25
TITLE:       Fixed NOT NULL fields in virtual tables
DESCRIPTION:
    Fields MON$SEC_DATABASE and MON$FILE_ID (from MON$SEC_DATABASE) were displayed in SQLDA as NULLABLE
    since shared metacache was introduced (6.0.0.1771).
NOTES:
    Original letter to FB-team: 10.05.2026 2214, subj:
    "shared-metacache: weird SQLDA for query to mon$database ( MON$FILE_ID & MON$SEC_DATABASE )"
    [26.05.2025] pzotov
    Confirmed bug on 6.0.0.1771, 6.0.0.1959.
    Checked on 6.0.0.1965-f9a8d1a.
"""

import pytest
from firebird.qa import *

test_sql = f"""
    set bail on;
    set heading off;
    set autoddl off;
    commit;
    create view v_info as
    select
        rr.rdb$relation_type as rel_type
       ,trim(ri.rdb$index_name) as idx_name
       ,coalesce(upper(ri.rdb$expression_source), rs.rdb$field_name) as idx_key
       ,coalesce(rc.rdb$constraint_type,'') constrt_type
       ,coalesce(rdb$unique_flag,0) as is_unique
       ,sign(octet_length(coalesce(rdb$expression_source,''))) is_computed
       ,sign(octet_length(coalesce(rdb$condition_source,''))) is_partial
    from rdb$relations rr
    join rdb$indices ri using(rdb$relation_name)
    left join rdb$relation_constraints rc using(rdb$index_name)
    left join rdb$index_segments rs using(rdb$index_name)
    where rr.rdb$relation_name = ?
    order by idx_name
    ;

    create table test (
        f01 varbinary(16)
    );
    commit;

    insert into test (f01)
    select gen_uuid()
    from generate_series(1, 500000) s(n);
    commit;

    -- crash was here:
    create index test_f01 on test(f01);
    commit;
"""

db = db_factory()
act = isql_act('db', test_sql)

@pytest.mark.version('>=6')
def test_1(act: Action):
    act.expected_stdout = f"""
    """
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
