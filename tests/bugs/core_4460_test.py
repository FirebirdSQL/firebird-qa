#coding:utf-8

"""
ID:          issue-4780
ISSUE:       4780
TITLE:       Expressions containing some built-in functions may be badly optimized
DESCRIPTION:
JIRA:        CORE-4460
FBTEST:      bugs.core_4460
NOTES:
    [25.07.2025] pzotov
    Separated expected output on major versions (4.x ... 6.x).
    Test probably will be further reimplemented, including adding checks for other functions.
    Issues exist for 4.x and 5.x: blob_append - currently it prevents index usage.

    Checked on 6.0.0.1061; 5.0.3.1686; 4.0.6.3223.
"""

import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db', substitutions=[('RDB\\$INDEX_\\d+', 'RDB_INDEX_*')])

@pytest.mark.version('>=4.0')
def test_1(act: Action):

    SQL_SCHEMA_SUFFIX = '' if act.is_version('<6') else " and dt.schema_name = 'SYSTEM'"
    RDB_SCHEMA_FIELD = "''" if act.is_version('<6') else 'rdb$schema_name'
    test_script = f"""
        set planonly;
        select * from (
           select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r01
           union
           select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f01
        ) as dt (name, schema_name) where dt.name='' {SQL_SCHEMA_SUFFIX}
        ;
        select * from (
          select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r02
          union
          select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f02
        ) as dt (name, schema_name) where dt.name = left('', 0) {SQL_SCHEMA_SUFFIX}
        ;

        select * from (
          select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r03
          union
          select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f03
        ) as dt (name, schema_name) where dt.name = minvalue('', '') {SQL_SCHEMA_SUFFIX}
        ;

        select * from (
          select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r04
          union
          select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f04
        ) as dt (name, schema_name) where dt.name = rpad('', 0, '') {SQL_SCHEMA_SUFFIX}
        ;

        select * from (
          select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r05
          union
          select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f05
        ) as dt (name, schema_name) where dt.name = blob_append('', 'foo', 'bar') {SQL_SCHEMA_SUFFIX}
        ;

        select * from (
          select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r07
          union
          select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f07
        ) as dt (name, schema_name) where dt.name = decode(octet_length(gen_uuid()), 16, 'foo', 'bar') {SQL_SCHEMA_SUFFIX}
        ;

        select * from (
          select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r08
          union
          select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f08
        ) as dt (name, schema_name) where dt.name = coalesce(gen_uuid(), 'bar') {SQL_SCHEMA_SUFFIX}
        ;

        select * from (
          select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r09
          union
          select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f09
        ) as dt (name, schema_name) where dt.name = nullif(gen_uuid(), 'bar') {SQL_SCHEMA_SUFFIX}
        ;

        select * from (
          select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r10
          union
          select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f10
        ) as dt (name, schema_name) where dt.name = crypt_hash(gen_uuid() using sha512) {SQL_SCHEMA_SUFFIX}
        ;
    """

    if act.is_version('<5'):
        pass
    else:
        test_script += f"""
            select * from (
              select rdb$relation_name, {RDB_SCHEMA_FIELD} from rdb$relations r51
              union
              select rdb$field_name, {RDB_SCHEMA_FIELD} from rdb$fields f51
            ) as dt (name, schema_name) where dt.name = unicode_char(0x227b) {SQL_SCHEMA_SUFFIX}
            ;
        """


    expected_stdout_4x = """
        PLAN SORT (DT R01 INDEX (RDB_INDEX_*), DT F01 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R02 INDEX (RDB_INDEX_*), DT F02 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R03 INDEX (RDB_INDEX_*), DT F03 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R04 INDEX (RDB_INDEX_*), DT F04 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R05 NATURAL, DT F05 NATURAL)
        PLAN SORT (DT R07 INDEX (RDB_INDEX_*), DT F07 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R08 INDEX (RDB_INDEX_*), DT F08 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R09 INDEX (RDB_INDEX_*), DT F09 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R10 INDEX (RDB_INDEX_*), DT F10 INDEX (RDB_INDEX_*))
    """

    expected_stdout_5x = """
        PLAN SORT (DT R01 INDEX (RDB_INDEX_*), DT F01 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R02 INDEX (RDB_INDEX_*), DT F02 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R03 INDEX (RDB_INDEX_*), DT F03 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R04 INDEX (RDB_INDEX_*), DT F04 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R05 NATURAL, DT F05 NATURAL)
        PLAN SORT (DT R07 INDEX (RDB_INDEX_*), DT F07 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R08 INDEX (RDB_INDEX_*), DT F08 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R09 INDEX (RDB_INDEX_*), DT F09 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R10 INDEX (RDB_INDEX_*), DT F10 INDEX (RDB_INDEX_*))
        PLAN SORT (DT R51 INDEX (RDB_INDEX_*), DT F51 INDEX (RDB_INDEX_*))
    """

    expected_stdout_6x = """
        PLAN SORT ("DT" "R01" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F01" INDEX ("SYSTEM"."RDB_INDEX_*"))
        PLAN SORT ("DT" "R02" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F02" INDEX ("SYSTEM"."RDB_INDEX_*"))
        PLAN SORT ("DT" "R03" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F03" INDEX ("SYSTEM"."RDB_INDEX_*"))
        PLAN SORT ("DT" "R04" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F04" INDEX ("SYSTEM"."RDB_INDEX_*"))
        PLAN SORT ("DT" "R05" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F05" INDEX ("SYSTEM"."RDB_INDEX_*"))
        PLAN SORT ("DT" "R07" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F07" INDEX ("SYSTEM"."RDB_INDEX_*"))
        PLAN SORT ("DT" "R08" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F08" INDEX ("SYSTEM"."RDB_INDEX_*"))
        PLAN SORT ("DT" "R09" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F09" INDEX ("SYSTEM"."RDB_INDEX_*"))
        PLAN SORT ("DT" "R10" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F10" INDEX ("SYSTEM"."RDB_INDEX_*"))
        PLAN SORT ("DT" "R51" INDEX ("SYSTEM"."RDB_INDEX_*"), "DT" "F51" INDEX ("SYSTEM"."RDB_INDEX_*"))
    """

    act.expected_stdout = expected_stdout_4x if act.is_version('<5') else expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
