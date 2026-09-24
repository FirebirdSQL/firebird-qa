#coding:utf-8

"""
ID:          functional.dsql.grouping_sets
TITLE:       GROUPING SETS, ROLLUP, CUBE, GROUPING_ID, window functions and positional ORDER BY regressions
DESCRIPTION:
  Functional coverage for the GROUP BY extensions GROUPING SETS, ROLLUP and CUBE.

  The test data intentionally contains:
    * several normal dimension values,
    * real NULL values in grouping columns,
    * two fiscal years to verify WHERE filtering before aggregation,
    * totals where positional ORDER BY can detect leaked hidden grouping columns,
    * a second table dedicated to mixed grouping items such as
      GROUP BY a, ROLLUP(b, c), CUBE(e, f).

  The positional ORDER BY assertions are regression checks. They are intended to
  catch bugs where internally added hidden grouping columns are incorrectly counted
  as visible select-list columns, e.g. ORDER BY 1 sorting by a hidden column instead
  of the first expression specified by the user.

  The mixed grouping and GROUPING_ID assertions verify the expansion of independent
  grouping items and the bit order of GROUPING_ID(). The window-function assertion
  verifies that grouped rows can be consumed by analytic/window functions without
  hidden grouping columns leaking into the visible result shape or sort positions.
  PSQL assertions verify that lowered GROUP BY extensions compile into ordinary
  BLR for stored procedures, triggers and EXECUTE BLOCK.
NOTES:
  Adjust the version marker below if GROUPING SETS is introduced in a different
  Firebird major/minor version in your branch.
"""

from decimal import Decimal

import pytest
from firebird.qa import *


init_script = """
    create table gs_sales (
        id integer not null primary key,
        region varchar(10),
        dept varchar(10),
        product varchar(10),
        fiscal_year integer not null,
        qty integer not null,
        amount integer not null
    );

    insert into gs_sales values (1,  'NORTH', 'HARDWARE', 'HAMMER', 2024, 2, 20);
    insert into gs_sales values (2,  'NORTH', 'HARDWARE', 'SAW',    2024, 1, 15);
    insert into gs_sales values (3,  'NORTH', 'SOFTWARE', 'IDE',    2024, 3, 60);
    insert into gs_sales values (4,  'SOUTH', 'HARDWARE', 'HAMMER', 2024, 4, 40);
    insert into gs_sales values (5,  'SOUTH', 'SOFTWARE', 'IDE',    2024, 2, 50);
    insert into gs_sales values (6,  'SOUTH', 'SOFTWARE', 'IDE',    2025, 1, 30);
    insert into gs_sales values (7,  'EAST',  'HARDWARE', 'SAW',    2024, 5, 25);
    insert into gs_sales values (8,  'EAST',  null,       'HAMMER', 2024, 1, 10);
    insert into gs_sales values (9,  null,    'HARDWARE', 'HAMMER', 2024, 1, 12);
    insert into gs_sales values (10, 'NORTH', 'HARDWARE', 'HAMMER', 2025, 1, 22);

    create table gs_mix_sales (
        id integer not null primary key,
        a varchar(10) not null,
        b varchar(10) not null,
        c varchar(10) not null,
        e varchar(10) not null,
        f varchar(10) not null,
        amount integer not null
    );

    insert into gs_mix_sales values (1, 'A', 'B1', 'C1', 'E1', 'F1', 10);
    insert into gs_mix_sales values (2, 'A', 'B1', 'C2', 'E1', 'F2', 20);
    insert into gs_mix_sales values (3, 'A', 'B2', 'C1', 'E2', 'F1', 30);
    insert into gs_mix_sales values (4, 'Z', 'B1', 'C1', 'E1', 'F1', 40);

    create table gs_regression_sales (
        id integer not null primary key,
        region varchar(10),
        dept varchar(10),
        product varchar(10),
        sold_at date not null,
        amount integer not null
    );

    insert into gs_regression_sales values (1, 'NORTH', 'HARDWARE', 'HAMMER', date '2024-01-10', 20);
    insert into gs_regression_sales values (2, 'NORTH', 'HARDWARE', 'SAW',    date '2024-01-11', 15);
    insert into gs_regression_sales values (3, 'NORTH', 'SOFTWARE', 'IDE',    date '2024-02-01', 60);
    insert into gs_regression_sales values (4, 'SOUTH', 'HARDWARE', 'HAMMER', date '2024-02-05', 40);
    insert into gs_regression_sales values (5, 'SOUTH', 'SOFTWARE', 'IDE',    date '2025-03-01', 30);
    insert into gs_regression_sales values (6, 'EAST',  'HARDWARE', 'SAW',    date '2025-03-03', 25);

    create table gs_invalid_sales (
        id integer not null primary key,
        region varchar(10),
        dept varchar(10),
        product varchar(10),
        amount integer not null
    );

    insert into gs_invalid_sales values (1, 'NORTH', 'HARDWARE', 'HAMMER', 20);
    insert into gs_invalid_sales values (2, 'NORTH', 'HARDWARE', 'SAW',    15);
    insert into gs_invalid_sales values (3, 'NORTH', 'SOFTWARE', 'IDE',    60);
    insert into gs_invalid_sales values (4, 'SOUTH', 'HARDWARE', 'HAMMER', 40);
    insert into gs_invalid_sales values (5, 'SOUTH', 'SOFTWARE', 'IDE',    50);

    create table gs_no_gid_sales (
        id integer not null primary key,
        region varchar(10),
        dept varchar(10),
        sold_at date not null,
        amount integer not null
    );

    insert into gs_no_gid_sales values (1, 'NORTH', 'HARDWARE', date '2024-01-10', 20);
    insert into gs_no_gid_sales values (2, 'NORTH', 'HARDWARE', date '2024-01-11', 15);
    insert into gs_no_gid_sales values (3, 'NORTH', 'SOFTWARE', date '2024-02-01', 60);
    insert into gs_no_gid_sales values (4, 'SOUTH', 'HARDWARE', date '2024-02-05', 40);
    insert into gs_no_gid_sales values (5, 'SOUTH', 'SOFTWARE', date '2025-03-01', 30);
    insert into gs_no_gid_sales values (6, 'EAST',  'HARDWARE', date '2025-03-03', 25);

    create table gs_no_gid_mix_sales (
        id integer not null primary key,
        a varchar(10) not null,
        b varchar(10) not null,
        c varchar(10) not null,
        e varchar(10) not null,
        f varchar(10) not null,
        amount integer not null
    );

    insert into gs_no_gid_mix_sales values (1, 'A', 'B1', 'C1', 'E1', 'F1', 10);
    insert into gs_no_gid_mix_sales values (2, 'A', 'B1', 'C2', 'E1', 'F2', 20);
    insert into gs_no_gid_mix_sales values (3, 'A', 'B2', 'C1', 'E2', 'F1', 30);
    insert into gs_no_gid_mix_sales values (4, 'Z', 'B1', 'C1', 'E1', 'F1', 40);

    create table gs_psql_trigger_log (
        id integer not null primary key,
        amount_sum integer
    );

    commit;
"""

# Python copy of GS_MIX_SALES, used to derive the expected result for mixed
# grouping items. Keeping this separate from the SQL query avoids hard-coding a
# very long expected list while still making the intended GROUP BY expansion clear.
MIX_ROWS = [
    ('A', 'B1', 'C1', 'E1', 'F1', 10),
    ('A', 'B1', 'C2', 'E1', 'F2', 20),
    ('A', 'B2', 'C1', 'E2', 'F1', 30),
    ('Z', 'B1', 'C1', 'E1', 'F1', 40),
]


db = db_factory(init=init_script)
act = python_act('db')


def _normalize_value(value):
    if isinstance(value, Decimal) and value == value.to_integral_value():
        return int(value)
    return value


def _fetch_rows(act, sql):
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute(sql)
        return [tuple(_normalize_value(value) for value in row) for row in cur.fetchall()]


def _assert_rows(act, label, sql, expected):
    actual = _fetch_rows(act, sql)
    assert actual == expected, (
        f"\n{label}\n"
        f"Expected:\n{expected!r}\n"
        f"Actual:\n{actual!r}\n"
    )


def _assert_sql_fails(act, sql):
    """Prepare/execute SQL and require an engine-side failure."""
    with act.db.connect() as con:
        cur = con.cursor()
        with pytest.raises(Exception) as exc_info:
            cur.execute(sql)
            cur.fetchall()

    assert str(exc_info.value), 'Expected a non-empty diagnostic for rejected SQL.'


def _grouping_id(*flags):
    """GROUPING_ID bit order: first argument is the most significant bit."""
    value = 0
    for flag in flags:
        value = value * 2 + flag
    return value


def _nulls_first(value):
    return (value is not None, value)


def _expected_mixed_grouping_rows():
    # GROUP BY a, ROLLUP(b, c), CUBE(e, f) expands to:
    #   a is always grouped normally,
    #   rollup(b, c) -> (b, c), (b), (),
    #   cube(e, f)   -> (e, f), (e), (f), ().
    rollup_bc_flags = [
        (0, 0),
        (0, 1),
        (1, 1),
    ]
    cube_ef_flags = [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]

    expected = []
    for gb, gc in rollup_bc_flags:
        for ge, gf in cube_ef_flags:
            flags = (0, gb, gc, ge, gf)
            groups = {}
            for a, b, c, e, f, amount in MIX_ROWS:
                key = (
                    a,
                    None if gb else b,
                    None if gc else c,
                    None if ge else e,
                    None if gf else f,
                )
                groups.setdefault(key, [0, 0])
                groups[key][0] += amount
                groups[key][1] += 1

            gid = _grouping_id(*flags)
            for key, (amount_sum, row_counts) in groups.items():
                expected.append((gid, *flags, *key, amount_sum, row_counts))

    expected.sort(
        key=lambda row: (
            row[6],      # a
            row[0],      # grouping_id(a, b, c, e, f)
            _nulls_first(row[7]),
            _nulls_first(row[8]),
            _nulls_first(row[9]),
            _nulls_first(row[10]),
        )
    )
    return expected


def _expected_mixed_grouping_rows_without_grouping_id():
    rollup_bc_flags = [
        (0, 0),
        (0, 1),
        (1, 1),
    ]
    cube_ef_flags = [
        (0, 0),
        (0, 1),
        (1, 0),
        (1, 1),
    ]

    expected = []
    for gb, gc in rollup_bc_flags:
        for ge, gf in cube_ef_flags:
            groups = {}
            for a, b, c, e, f, amount in MIX_ROWS:
                key = (
                    a,
                    None if gb else b,
                    None if gc else c,
                    None if ge else e,
                    None if gf else f,
                )
                groups.setdefault(key, [0, 0])
                groups[key][0] += amount
                groups[key][1] += 1

            for key, (amount_sum, row_counts) in groups.items():
                expected.append((gb, gc, ge, gf, *key, amount_sum, row_counts))

    expected.sort(
        key=lambda row: (
            row[4],  # a
            row[0],  # grouping(b)
            row[1],  # grouping(c)
            row[2],  # grouping(e)
            row[3],  # grouping(f)
            _nulls_first(row[5]),
            _nulls_first(row[6]),
            _nulls_first(row[7]),
            _nulls_first(row[8]),
        )
    )
    return expected


INVALID_EXTENSION_PLACEMENT = [
    pytest.param(
        """
        select rollup(region)
        from gs_invalid_sales
        """,
        id='rollup_in_select_list',
    ),
    pytest.param(
        """
        select cube(region, dept)
        from gs_invalid_sales
        """,
        id='cube_in_select_list',
    ),
    pytest.param(
        """
        select id
        from gs_invalid_sales
        where rollup(region) is not null
        """,
        id='rollup_in_where',
    ),
    pytest.param(
        """
        select id
        from gs_invalid_sales
        order by cube(region, dept)
        """,
        id='cube_in_order_by',
    ),
    pytest.param(
        """
        select region, cast(sum(amount) as integer)
        from gs_invalid_sales
        group by region
        having grouping sets ((region)) is not null
        """,
        id='grouping_sets_in_having_expression',
    ),
]


INVALID_GROUP_BY_SYNTAX = [
    pytest.param(
        """
        select region, cast(sum(amount) as integer)
        from gs_invalid_sales
        group by grouping sets region
        """,
        id='grouping_sets_without_parenthesized_list',
    ),
    pytest.param(
        """
        select region, cast(sum(amount) as integer)
        from gs_invalid_sales
        group by grouping sets ((region),)
        """,
        id='grouping_sets_trailing_comma',
    ),
    pytest.param(
        """
        select region, cast(sum(amount) as integer)
        from gs_invalid_sales
        group by rollup(region,)
        """,
        id='rollup_trailing_comma',
    ),
    pytest.param(
        """
        select region, dept, cast(sum(amount) as integer)
        from gs_invalid_sales
        group by cube(, region, dept)
        """,
        id='cube_leading_comma',
    ),
    pytest.param(
        """
        select cast(sum(amount) as integer)
        from gs_invalid_sales
        group by grouping sets ()
        """,
        id='empty_grouping_sets_list',
    ),
]


INVALID_GROUPING_FUNCTION_USAGE = [
    pytest.param(
        """
        select grouping(region)
        from gs_invalid_sales
        """,
        id='grouping_without_extended_group_by',
    ),
    pytest.param(
        """
        select region, cast(grouping(dept) as integer), cast(sum(amount) as integer)
        from gs_invalid_sales
        group by region
        """,
        id='grouping_argument_not_in_extended_grouping',
    ),
    pytest.param(
        """
        select region, cast(grouping_id(region, dept) as integer), cast(sum(amount) as integer)
        from gs_invalid_sales
        group by region
        """,
        id='grouping_id_without_extended_grouping',
    ),
    pytest.param(
        """
        select region, cast(grouping_id(region, dept) as integer), cast(sum(amount) as integer)
        from gs_invalid_sales
        group by cube(region)
        """,
        id='grouping_id_argument_missing_from_grouping_item',
    ),
    pytest.param(
        """
        select region, cast(grouping_id(upper(region)) as integer), cast(sum(amount) as integer)
        from gs_invalid_sales
        group by cube(region)
        """,
        id='grouping_id_expression_not_matching_grouping_expression',
    ),
    pytest.param(
        """
        select region, cast(grouping(region, dept) as integer), cast(sum(amount) as integer)
        from gs_invalid_sales
        group by cube(region)
        """,
        id='multiargument_grouping_argument_missing_from_grouping_item',
    ),
    pytest.param(
        """
        select region, cast(sum(amount) as integer)
        from gs_invalid_sales
        where grouping(region) = 0
        group by rollup(region)
        """,
        id='grouping_function_in_where',
    ),
]


INVALID_GROUP_BY_SEMANTICS = [
    pytest.param(
        """
        select region, dept, amount
        from gs_invalid_sales
        group by rollup(region, dept)
        """,
        id='non_aggregated_measure_not_grouped',
    ),
    pytest.param(
        """
        select region, product, cast(sum(amount) as integer)
        from gs_invalid_sales
        group by cube(region, dept)
        """,
        id='non_aggregated_dimension_not_grouped',
    ),
    pytest.param(
        """
        select region, cast(sum(amount) as integer)
        from gs_invalid_sales
        group by rollup(dept)
        """,
        id='select_column_not_covered_by_rollup',
    ),
]


@pytest.mark.version('>=6.0')
def test_1_basic_grouping_sets_rollup_cube_and_regressions(act: Action):
    # 1. Explicit GROUPING SETS:
    #    (region, dept), (region), (dept), ().
    #    GROUPING() flags distinguish subtotal NULLs from real data NULLs.
    _assert_rows(
        act,
        'explicit grouping sets with real NULL values and grand total',
        """
        select
            cast(grouping(region) as integer) as g_region,
            cast(grouping(dept) as integer) as g_dept,
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum,
            cast(count(*) as integer) as row_counts
        from gs_sales
        where fiscal_year = 2024
        group by grouping sets ((region, dept), (region), (dept), ())
        order by g_region, g_dept, region nulls first, dept nulls first
        """,
        [
            (0, 0, None,    'HARDWARE',  12, 1),
            (0, 0, 'EAST',  None,        10, 1),
            (0, 0, 'EAST',  'HARDWARE',  25, 1),
            (0, 0, 'NORTH', 'HARDWARE',  35, 2),
            (0, 0, 'NORTH', 'SOFTWARE',  60, 1),
            (0, 0, 'SOUTH', 'HARDWARE',  40, 1),
            (0, 0, 'SOUTH', 'SOFTWARE',  50, 1),
            (0, 1, None,    None,        12, 1),
            (0, 1, 'EAST',  None,        35, 2),
            (0, 1, 'NORTH', None,        95, 3),
            (0, 1, 'SOUTH', None,        90, 2),
            (1, 0, None,    None,        10, 1),
            (1, 0, None,    'HARDWARE', 112, 5),
            (1, 0, None,    'SOFTWARE', 110, 2),
            (1, 1, None,    None,       232, 8),
        ],
    )

    # 2. ROLLUP(region, dept) should produce:
    #    (region, dept), (region), ().
    _assert_rows(
        act,
        'rollup(region, dept)',
        """
        select
            cast(grouping(region) as integer) as g_region,
            cast(grouping(dept) as integer) as g_dept,
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum,
            cast(count(*) as integer) as row_counts
        from gs_sales
        where fiscal_year = 2024
        group by rollup(region, dept)
        order by g_region, g_dept, region nulls first, dept nulls first
        """,
        [
            (0, 0, None,    'HARDWARE',  12, 1),
            (0, 0, 'EAST',  None,        10, 1),
            (0, 0, 'EAST',  'HARDWARE',  25, 1),
            (0, 0, 'NORTH', 'HARDWARE',  35, 2),
            (0, 0, 'NORTH', 'SOFTWARE',  60, 1),
            (0, 0, 'SOUTH', 'HARDWARE',  40, 1),
            (0, 0, 'SOUTH', 'SOFTWARE',  50, 1),
            (0, 1, None,    None,        12, 1),
            (0, 1, 'EAST',  None,        35, 2),
            (0, 1, 'NORTH', None,        95, 3),
            (0, 1, 'SOUTH', None,        90, 2),
            (1, 1, None,    None,       232, 8),
        ],
    )

    # 3. CUBE(region, dept) is equivalent to the four explicit grouping sets
    #    above for two dimensions.
    _assert_rows(
        act,
        'cube(region, dept)',
        """
        select
            cast(grouping(region) as integer) as g_region,
            cast(grouping(dept) as integer) as g_dept,
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum,
            cast(count(*) as integer) as row_counts
        from gs_sales
        where fiscal_year = 2024
        group by cube(region, dept)
        order by g_region, g_dept, region nulls first, dept nulls first
        """,
        [
            (0, 0, None,    'HARDWARE',  12, 1),
            (0, 0, 'EAST',  None,        10, 1),
            (0, 0, 'EAST',  'HARDWARE',  25, 1),
            (0, 0, 'NORTH', 'HARDWARE',  35, 2),
            (0, 0, 'NORTH', 'SOFTWARE',  60, 1),
            (0, 0, 'SOUTH', 'HARDWARE',  40, 1),
            (0, 0, 'SOUTH', 'SOFTWARE',  50, 1),
            (0, 1, None,    None,        12, 1),
            (0, 1, 'EAST',  None,        35, 2),
            (0, 1, 'NORTH', None,        95, 3),
            (0, 1, 'SOUTH', None,        90, 2),
            (1, 0, None,    None,        10, 1),
            (1, 0, None,    'HARDWARE', 112, 5),
            (1, 0, None,    'SOFTWARE', 110, 2),
            (1, 1, None,    None,       232, 8),
        ],
    )

    # 4. Focused NULL-disambiguation check:
    #    Both rows below have REGION = NULL, but only the second one is the grand total.
    _assert_rows(
        act,
        'GROUPING() must distinguish real NULL data from subtotal NULL',
        """
        select
            cast(grouping(region) as integer) as g_region,
            region,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
        group by grouping sets ((region), ())
        order by g_region, region nulls first
        """,
        [
            (0, None,     12),
            (0, 'EAST',   35),
            (0, 'NORTH',  95),
            (0, 'SOUTH',  90),
            (1, None,    232),
        ],
    )

    # 5. HAVING must be applied to every grouping set, including subtotals.
    _assert_rows(
        act,
        'HAVING with grouping sets',
        """
        select
            cast(grouping(region) as integer) as g_region,
            cast(grouping(dept) as integer) as g_dept,
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
        group by grouping sets ((region, dept), (region), ())
        having sum(amount) >= 90
        order by g_region, g_dept, region nulls first, dept nulls first
        """,
        [
            (0, 1, 'NORTH', None,  95),
            (0, 1, 'SOUTH', None,  90),
            (1, 1, None,    None, 232),
        ],
    )

    # 6. Regression: ordinary GROUP BY / HAVING / positional ORDER BY
    #    must remain unchanged.
    _assert_rows(
        act,
        'ordinary group by with having and order by positions',
        """
        select
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
        group by region, dept
        having sum(amount) >= 35
        order by 3 desc, 1, 2
        """,
        [
            ('NORTH', 'SOFTWARE', 60),
            ('SOUTH', 'SOFTWARE', 50),
            ('SOUTH', 'HARDWARE', 40),
            ('NORTH', 'HARDWARE', 35),
        ],
    )

    # 7. Regression: ORDER BY 1 in a GROUPING SETS query must use the first
    #    visible select-list item (REGION), not an internally added hidden column.
    #    REGION is NULL for the grand total, so with NULLS FIRST the total row
    #    must be first.
    _assert_rows(
        act,
        'grouping sets order by visible column position 1',
        """
        select
            region,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region is not null
        group by grouping sets ((region), ())
        order by 1 nulls first
        """,
        [
            (None,    220),
            ('EAST',   35),
            ('NORTH',  95),
            ('SOUTH',  90),
        ],
    )

    # 8. Regression: ORDER BY 2 must use AMOUNT_SUM, not REGION or a hidden column.
    _assert_rows(
        act,
        'grouping sets order by visible column position 2',
        """
        select
            region,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region is not null
        group by grouping sets ((region), ())
        order by 2 desc
        """,
        [
            (None,    220),
            ('NORTH',  95),
            ('SOUTH',  90),
            ('EAST',   35),
        ],
    )

    # 9. Regression: ORDER BY position must also work when GROUPING() is visible.
    #    Here ORDER BY 3 must sort by AMOUNT_SUM.
    _assert_rows(
        act,
        'grouping sets with visible grouping flag and order by position 3',
        """
        select
            cast(grouping(region) as integer) as g_region,
            region,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region is not null
        group by grouping sets ((region), ())
        order by 3 desc
        """,
        [
            (1, None,    220),
            (0, 'NORTH',  95),
            (0, 'SOUTH',  90),
            (0, 'EAST',   35),
        ],
    )


@pytest.mark.version('>=6.0')
def test_2_grouping_id_bit_order(act: Action):
    # GROUPING_ID(region, dept) must match the GROUPING() flags where REGION is
    # the most significant bit and DEPT is the least significant bit:
    #   detail           -> 0b00 = 0
    #   region subtotal  -> 0b01 = 1
    #   dept subtotal    -> 0b10 = 2
    #   grand total      -> 0b11 = 3
    _assert_rows(
        act,
        'GROUPING_ID bit order for CUBE(region, dept)',
        """
        select
            cast(grouping(region) as integer) as g_region,
            cast(grouping(dept) as integer) as g_dept,
            cast(grouping_id(region, dept) as integer) as gid,
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
        group by cube(region, dept)
        order by gid, region nulls first, dept nulls first
        """,
        [
            (0, 0, 0, None,    'HARDWARE',  12),
            (0, 0, 0, 'EAST',  None,        10),
            (0, 0, 0, 'EAST',  'HARDWARE',  25),
            (0, 0, 0, 'NORTH', 'HARDWARE',  35),
            (0, 0, 0, 'NORTH', 'SOFTWARE',  60),
            (0, 0, 0, 'SOUTH', 'HARDWARE',  40),
            (0, 0, 0, 'SOUTH', 'SOFTWARE',  50),
            (0, 1, 1, None,    None,        12),
            (0, 1, 1, 'EAST',  None,        35),
            (0, 1, 1, 'NORTH', None,        95),
            (0, 1, 1, 'SOUTH', None,        90),
            (1, 0, 2, None,    None,        10),
            (1, 0, 2, None,    'HARDWARE', 112),
            (1, 0, 2, None,    'SOFTWARE', 110),
            (1, 1, 3, None,    None,       232),
        ],
    )


@pytest.mark.version('>=6.0')
def test_3_mixed_grouping_items_with_rollup_and_cube(act: Action):
    # Mixed grouping items: one ordinary grouping item, one ROLLUP, and one CUBE.
    # This covers the syntax shape:
    #   GROUP BY a, ROLLUP(b, c), CUBE(e, f)
    # and verifies that GROUPING_ID(a, b, c, e, f) follows the same flags as
    # GROUPING() for all expanded grouping sets.
    _assert_rows(
        act,
        'mixed group by items: a, rollup(b, c), cube(e, f)',
        """
        select
            cast(grouping_id(a, b, c, e, f) as integer) as gid,
            cast(grouping(a) as integer) as ga,
            cast(grouping(b) as integer) as gb,
            cast(grouping(c) as integer) as gc,
            cast(grouping(e) as integer) as ge,
            cast(grouping(f) as integer) as gf,
            a,
            b,
            c,
            e,
            f,
            cast(sum(amount) as integer) as amount_sum,
            cast(count(*) as integer) as row_counts
        from gs_mix_sales
        group by a, rollup(b, c), cube(e, f)
        order by a, gid, b nulls first, c nulls first, e nulls first, f nulls first
        """,
        _expected_mixed_grouping_rows(),
    )

    # Positional ORDER BY must continue to count only visible columns even when
    # mixed grouping items require several hidden grouping expressions internally.
    _assert_rows(
        act,
        'mixed grouping order by visible select-list positions',
        """
        select
            a,
            cast(grouping_id(a, b, c, e, f) as integer) as gid,
            cast(sum(amount) as integer) as amount_sum
        from gs_mix_sales
        group by a, rollup(b, c), cube(e, f)
        order by 1 desc, 2 desc, 3 desc
        rows 6
        """,
        [
            ('Z', 15, 40),
            ('Z', 14, 40),
            ('Z', 13, 40),
            ('Z', 12, 40),
            ('Z', 7, 40),
            ('Z', 6, 40),
        ],
    )


@pytest.mark.version('>=6.0')
def test_4_window_functions_over_grouped_rows(act: Action):
    # Window functions over the grouped result. The inner query produces the
    # GROUPING SETS/CUBE rows; the outer query applies analytic functions to those
    # rows. This is the practical shape used by applications that rank detail rows,
    # subtotal rows and total rows independently.
    _assert_rows(
        act,
        'window functions over cube result partitioned by GROUPING_ID',
        """
        select
            gid,
            region,
            dept,
            amount_sum,
            cast(sum(amount_sum) over (partition by gid) as integer) as gid_level_total,
            cast(row_number() over (
                partition by gid
                order by amount_sum desc, region nulls first, dept nulls first
            ) as integer) as rn_in_gid
        from (
            select
                cast(grouping_id(region, dept) as integer) as gid,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum
            from gs_sales
            where fiscal_year = 2024
            group by cube(region, dept)
        ) q
        order by gid, rn_in_gid
        """,
        [
            (0, 'NORTH', 'SOFTWARE',  60, 232, 1),
            (0, 'SOUTH', 'SOFTWARE',  50, 232, 2),
            (0, 'SOUTH', 'HARDWARE',  40, 232, 3),
            (0, 'NORTH', 'HARDWARE',  35, 232, 4),
            (0, 'EAST',  'HARDWARE',  25, 232, 5),
            (0, None,    'HARDWARE',  12, 232, 6),
            (0, 'EAST',  None,        10, 232, 7),
            (1, 'NORTH', None,        95, 232, 1),
            (1, 'SOUTH', None,        90, 232, 2),
            (1, 'EAST',  None,        35, 232, 3),
            (1, None,    None,        12, 232, 4),
            (2, None,    'HARDWARE', 112, 232, 1),
            (2, None,    'SOFTWARE', 110, 232, 2),
            (2, None,    None,        10, 232, 3),
            (3, None,    None,       232, 232, 1),
        ],
    )

    # Positional ORDER BY in the outer query must refer to the visible outer
    # select-list, not to hidden columns inherited from grouped subqueries.
    _assert_rows(
        act,
        'window query order by visible positions after grouping sets subquery',
        """
        select
            gid,
            amount_sum,
            cast(row_number() over (partition by gid order by amount_sum desc) as integer) as rn_in_gid
        from (
            select
                cast(grouping_id(region, dept) as integer) as gid,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum
            from gs_sales
            where fiscal_year = 2024
            group by cube(region, dept)
        ) q
        order by 1 desc, 3, 2 desc
        rows 5
        """,
        [
            (3, 232, 1),
            (2, 112, 1),
            (2, 110, 2),
            (2, 10, 3),
            (1, 95, 1),
        ],
    )

@pytest.mark.version('>=6.0')
def test_5_hidden_grouping_columns_do_not_leak_from_derived_table(act: Action):
    _assert_rows(
        act,
        'hidden columns must not leak through derived table SELECT *',
        """
        select *
        from (
            select
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum
            from gs_regression_sales
            group by cube(region, dept)
        ) q
        order by region nulls first, dept nulls first, amount_sum
        """,
        [
            (None,    None,       190),
            (None,    'HARDWARE', 100),
            (None,    'SOFTWARE',  90),
            ('EAST',  None,        25),
            ('EAST',  'HARDWARE',  25),
            ('NORTH', None,        95),
            ('NORTH', 'HARDWARE',  35),
            ('NORTH', 'SOFTWARE',  60),
            ('SOUTH', None,        70),
            ('SOUTH', 'HARDWARE',  40),
            ('SOUTH', 'SOFTWARE',  30),
        ],
    )


@pytest.mark.version('>=6.0')
def test_6_hidden_grouping_columns_do_not_leak_from_cte(act: Action):
    _assert_rows(
        act,
        'hidden columns must not leak through CTE SELECT *',
        """
        with q as (
            select
                cast(grouping_id(region, dept) as integer) as gid,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum
            from gs_regression_sales
            group by cube(region, dept)
        )
        select *
        from q
        order by 1, 2 nulls first, 3 nulls first, 4
        """,
        [
            (0, 'EAST',  'HARDWARE',  25),
            (0, 'NORTH', 'HARDWARE',  35),
            (0, 'NORTH', 'SOFTWARE',  60),
            (0, 'SOUTH', 'HARDWARE',  40),
            (0, 'SOUTH', 'SOFTWARE',  30),
            (1, 'EAST',  None,        25),
            (1, 'NORTH', None,        95),
            (1, 'SOUTH', None,        70),
            (2, None,    'HARDWARE', 100),
            (2, None,    'SOFTWARE',  90),
            (3, None,    None,       190),
        ],
    )


@pytest.mark.version('>=6.0')
def test_7_grouping_id_is_usable_in_having(act: Action):
    _assert_rows(
        act,
        'GROUPING_ID in HAVING',
        """
        select
            cast(grouping_id(region, dept) as integer) as gid,
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum
        from gs_regression_sales
        group by cube(region, dept)
        having grouping_id(region, dept) in (1, 3)
        order by gid, region nulls first
        """,
        [
            (1, 'EAST',  None,  25),
            (1, 'NORTH', None,  95),
            (1, 'SOUTH', None,  70),
            (3, None,    None, 190),
        ],
    )


@pytest.mark.version('>=6.0')
def test_8_rollup_with_expressions_and_matching_grouping_id_arguments(act: Action):
    _assert_rows(
        act,
        'ROLLUP over expressions with GROUPING_ID on the same expressions',
        """
        select
            cast(grouping_id(extract(year from sold_at), upper(region)) as integer) as gid,
            cast(extract(year from sold_at) as integer) as sold_year,
            upper(region) as region_upper,
            cast(sum(amount) as integer) as amount_sum
        from gs_regression_sales
        group by rollup(extract(year from sold_at), upper(region))
        order by gid, sold_year nulls first, region_upper nulls first
        """,
        [
            (0, 2024, 'NORTH',  95),
            (0, 2024, 'SOUTH',  40),
            (0, 2025, 'EAST',   25),
            (0, 2025, 'SOUTH',  30),
            (1, 2024, None,    135),
            (1, 2025, None,     55),
            (3, None, None,    190),
        ],
    )


@pytest.mark.version('>=6.0')
def test_9_distinct_aggregate_and_count_star_with_rollup(act: Action):
    _assert_rows(
        act,
        'aggregate variants with ROLLUP',
        """
        select
            cast(grouping_id(region, dept) as integer) as gid,
            region,
            dept,
            cast(count(*) as integer) as row_counts,
            cast(count(distinct product) as integer) as distinct_products,
            cast(sum(amount) as integer) as amount_sum
        from gs_regression_sales
        group by rollup(region, dept)
        order by gid, region nulls first, dept nulls first
        """,
        [
            (0, 'EAST',  'HARDWARE', 1, 1,  25),
            (0, 'NORTH', 'HARDWARE', 2, 2,  35),
            (0, 'NORTH', 'SOFTWARE', 1, 1,  60),
            (0, 'SOUTH', 'HARDWARE', 1, 1,  40),
            (0, 'SOUTH', 'SOFTWARE', 1, 1,  30),
            (1, 'EAST',  None,       1, 1,  25),
            (1, 'NORTH', None,       3, 3,  95),
            (1, 'SOUTH', None,       2, 2,  70),
            (3, None,    None,       6, 3, 190),
        ],
    )


@pytest.mark.version('>=6.0')
def test_10_positional_order_by_with_alias_collision(act: Action):
    _assert_rows(
        act,
        'positional ORDER BY with potentially confusing aliases',
        """
        select
            s.region as amount_sum,
            cast(sum(s.amount) as integer) as region
        from gs_regression_sales s
        group by rollup(s.region)
        order by 1 nulls first, 2 desc
        """,
        [
            (None,    190),
            ('EAST',   25),
            ('NORTH',  95),
            ('SOUTH',  70),
        ],
    )


@pytest.mark.version('>=6.0')
@pytest.mark.parametrize('sql', INVALID_EXTENSION_PLACEMENT)
def test_11_grouping_extensions_rejected_outside_group_by(act: Action, sql: str):
    _assert_sql_fails(act, sql)


@pytest.mark.version('>=6.0')
@pytest.mark.parametrize('sql', INVALID_GROUP_BY_SYNTAX)
def test_12_malformed_group_by_extension_syntax_is_rejected(act: Action, sql: str):
    _assert_sql_fails(act, sql)


@pytest.mark.version('>=6.0')
@pytest.mark.parametrize('sql', INVALID_GROUPING_FUNCTION_USAGE)
def test_13_invalid_grouping_and_grouping_id_usage_is_rejected(act: Action, sql: str):
    _assert_sql_fails(act, sql)


@pytest.mark.version('>=6.0')
@pytest.mark.parametrize('sql', INVALID_GROUP_BY_SEMANTICS)
def test_14_extended_group_by_does_not_relax_standard_group_by_rules(act: Action, sql: str):
    _assert_sql_fails(act, sql)


@pytest.mark.version('>=6.0')
def test_15_mixed_grouping_without_grouping_id(act: Action):
    _assert_rows(
        act,
        'GROUP BY a, ROLLUP(b, c), CUBE(e, f) without GROUPING_ID()',
        """
        select
            cast(grouping(b) as integer) as g_b,
            cast(grouping(c) as integer) as g_c,
            cast(grouping(e) as integer) as g_e,
            cast(grouping(f) as integer) as g_f,
            a,
            b,
            c,
            e,
            f,
            cast(sum(amount) as integer) as amount_sum,
            cast(count(*) as integer) as row_counts
        from gs_no_gid_mix_sales
        group by a, rollup(b, c), cube(e, f)
        order by
            a,
            g_b,
            g_c,
            g_e,
            g_f,
            b nulls first,
            c nulls first,
            e nulls first,
            f nulls first
        """,
        _expected_mixed_grouping_rows_without_grouping_id(),
    )


@pytest.mark.version('>=6.0')
def test_16_window_functions_over_grouped_rows_without_grouping_id(act: Action):
    _assert_rows(
        act,
        'window functions over CUBE result without GROUPING_ID()',
        """
        with grouped as (
            select
                cast(grouping(region) as integer) as g_region,
                cast(grouping(dept) as integer) as g_dept,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum
            from gs_no_gid_sales
            group by cube(region, dept)
        )
        select
            g_region,
            g_dept,
            region,
            dept,
            amount_sum,
            cast(row_number() over (
                partition by g_region, g_dept
                order by amount_sum desc, region nulls first, dept nulls first
            ) as integer) as rn,
            cast(sum(amount_sum) over (partition by g_region, g_dept) as integer) as partition_sum
        from grouped
        order by g_region, g_dept, rn
        """,
        [
            (0, 0, 'NORTH', 'SOFTWARE',  60, 1, 190),
            (0, 0, 'SOUTH', 'HARDWARE',  40, 2, 190),
            (0, 0, 'NORTH', 'HARDWARE',  35, 3, 190),
            (0, 0, 'SOUTH', 'SOFTWARE',  30, 4, 190),
            (0, 0, 'EAST',  'HARDWARE',  25, 5, 190),
            (0, 1, 'NORTH', None,        95, 1, 190),
            (0, 1, 'SOUTH', None,        70, 2, 190),
            (0, 1, 'EAST',  None,        25, 3, 190),
            (1, 0, None,    'HARDWARE', 100, 1, 190),
            (1, 0, None,    'SOFTWARE',  90, 2, 190),
            (1, 1, None,    None,       190, 1, 190),
        ],
    )


@pytest.mark.version('>=6.0')
def test_17_rollup_with_expressions_without_grouping_id(act: Action):
    _assert_rows(
        act,
        'ROLLUP over expressions with GROUPING() only',
        """
        select
            cast(grouping(extract(year from sold_at)) as integer) as g_year,
            cast(grouping(upper(region)) as integer) as g_region_upper,
            cast(extract(year from sold_at) as integer) as sold_year,
            upper(region) as region_upper,
            cast(sum(amount) as integer) as amount_sum
        from gs_no_gid_sales
        group by rollup(extract(year from sold_at), upper(region))
        order by g_year, g_region_upper, sold_year nulls first, region_upper nulls first
        """,
        [
            (0, 0, 2024, 'NORTH',  95),
            (0, 0, 2024, 'SOUTH',  40),
            (0, 0, 2025, 'EAST',   25),
            (0, 0, 2025, 'SOUTH',  30),
            (0, 1, 2024, None,    135),
            (0, 1, 2025, None,     55),
            (1, 1, None, None,    190),
        ],
    )


@pytest.mark.version('>=6.0')
def test_18_positional_order_by_ignores_hidden_columns_without_grouping_id(act: Action):
    _assert_rows(
        act,
        'ORDER BY 1 with hidden grouping columns but without GROUPING_ID()',
        """
        select
            coalesce(region, '<TOTAL>') as visible_region,
            cast(sum(amount) as integer) as amount_sum
        from gs_no_gid_sales
        group by rollup(region)
        order by 1
        """,
        [
            ('<TOTAL>', 190),
            ('EAST',    25),
            ('NORTH',   95),
            ('SOUTH',   70),
        ],
    )


@pytest.mark.version('>=6.0')
def test_19_grouping_extensions_compile_in_selectable_procedure_blr(act: Action):
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            recreate procedure gs_psql_rollup_proc
            returns (
                gid integer,
                g_region integer,
                region varchar(10),
                amount_sum integer
            )
            as
            begin
                for
                    select
                        cast(grouping_id(region) as integer),
                        cast(grouping(region) as integer),
                        region,
                        cast(sum(amount) as integer)
                    from gs_sales
                    where fiscal_year = 2024
                      and region is not null
                    group by rollup(region)
                    order by 1, 3
                    into :gid, :g_region, :region, :amount_sum
                do
                    suspend;
            end
            """
        )
        con.commit()

    _assert_rows(
        act,
        'stored procedure BLR with ROLLUP, GROUPING and GROUPING_ID',
        """
        select gid, g_region, region, amount_sum
        from gs_psql_rollup_proc
        order by gid, region nulls first
        """,
        [
            (0, 0, 'EAST',   35),
            (0, 0, 'NORTH',  95),
            (0, 0, 'SOUTH',  90),
            (1, 1, None,    220),
        ],
    )


@pytest.mark.version('>=6.0')
def test_20_grouping_extensions_compile_in_execute_block(act: Action):
    _assert_rows(
        act,
        'EXECUTE BLOCK with GROUPING SETS and GROUPING_ID',
        """
        execute block
        returns (
            gid integer,
            dept varchar(10),
            amount_sum integer
        )
        as
        begin
            for
                select
                    cast(grouping_id(dept) as integer),
                    dept,
                    cast(sum(amount) as integer)
                from gs_sales
                where fiscal_year = 2024
                group by grouping sets ((dept), ())
                order by 1, 2 nulls first
                into :gid, :dept, :amount_sum
            do
                suspend;
        end
        """,
        [
            (0, None,        10),
            (0, 'HARDWARE', 112),
            (0, 'SOFTWARE', 110),
            (1, None,       232),
        ],
    )


@pytest.mark.version('>=6.0')
def test_21_grouping_extensions_compile_in_trigger_blr(act: Action):
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            recreate trigger gs_psql_trigger_log_bi for gs_psql_trigger_log
            active before insert
            as
            begin
                select cast(sum(amount) as integer)
                from gs_sales
                where fiscal_year = 2024
                group by rollup(region)
                having grouping(region) = 1
                into new.amount_sum;
            end
            """
        )
        cur.execute("delete from gs_psql_trigger_log")
        cur.execute("insert into gs_psql_trigger_log (id) values (1)")
        con.commit()

    _assert_rows(
        act,
        'trigger BLR with ROLLUP and GROUPING in HAVING',
        """
        select id, amount_sum
        from gs_psql_trigger_log
        """,
        [
            (1, 232),
        ],
    )


@pytest.mark.version('>=6.0')
def test_22_empty_grouping_set_and_duplicate_grouping_sets(act: Action):
    _assert_rows(
        act,
        'GROUP BY () returns one group for non-empty input',
        """
        select cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
        group by ()
        """,
        [
            (232,),
        ],
    )

    _assert_rows(
        act,
        'GROUP BY () returns one group for empty input',
        """
        select
            cast(count(*) as integer) as row_counts,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 1900
        group by ()
        """,
        [
            (0, None),
        ],
    )

    _assert_rows(
        act,
        'duplicate grouping sets are preserved by default',
        """
        select
            cast(grouping(region) as integer) as g_region,
            region,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region = 'NORTH'
        group by grouping sets ((region), (region), ())
        order by g_region, region nulls first
        """,
        [
            (0, 'NORTH', 95),
            (0, 'NORTH', 95),
            (1, None,    95),
        ],
    )

    _assert_rows(
        act,
        'GROUP BY DISTINCT removes duplicate grouping sets',
        """
        select
            cast(grouping(region) as integer) as g_region,
            region,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region = 'NORTH'
        group by distinct grouping sets ((region), (region), ())
        order by g_region, region nulls first
        """,
        [
            (0, 'NORTH', 95),
            (1, None,    95),
        ],
    )


@pytest.mark.version('>=6.0')
def test_23_grouping_functions_in_order_by_without_selecting_them(act: Action):
    _assert_rows(
        act,
        'ORDER BY GROUPING() without selecting the grouping flag',
        """
        select
            region,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region is not null
        group by grouping sets ((region), ())
        order by grouping(region) desc, region
        """,
        [
            (None,    220),
            ('EAST',   35),
            ('NORTH',  95),
            ('SOUTH',  90),
        ],
    )

    _assert_rows(
        act,
        'ORDER BY GROUPING_ID() without selecting the grouping id',
        """
        select
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region is not null
        group by cube(region, dept)
        order by grouping_id(region, dept), region, dept nulls first
        rows 8
        """,
        [
            ('EAST',  None,        10),
            ('EAST',  'HARDWARE',  25),
            ('NORTH', 'HARDWARE',  35),
            ('NORTH', 'SOFTWARE',  60),
            ('SOUTH', 'HARDWARE',  40),
            ('SOUTH', 'SOFTWARE',  50),
            ('EAST',  None,        35),
            ('NORTH', None,        95),
        ],
    )


@pytest.mark.version('>=6.0')
def test_24_grouping_extensions_compile_in_view_blr(act: Action):
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute(
            """
            recreate view gs_rollup_view (
                gid,
                g_region,
                region,
                amount_sum
            )
            as
            select
                cast(grouping_id(region) as integer),
                cast(grouping(region) as integer),
                region,
                cast(sum(amount) as integer)
            from gs_sales
            where fiscal_year = 2024
              and region is not null
            group by rollup(region)
            """
        )
        con.commit()

    _assert_rows(
        act,
        'view BLR with ROLLUP, GROUPING and GROUPING_ID',
        """
        select gid, g_region, region, amount_sum
        from gs_rollup_view
        order by gid, region nulls first
        """,
        [
            (0, 0, 'EAST',   35),
            (0, 0, 'NORTH',  95),
            (0, 0, 'SOUTH',  90),
            (1, 1, None,    220),
        ],
    )


@pytest.mark.version('>=6.0')
def test_25_select_distinct_ignores_hidden_grouping_columns(act: Action):
    _assert_rows(
        act,
        'SELECT DISTINCT must not include hidden grouping columns',
        """
        select distinct
            region
        from gs_sales
        where fiscal_year = 2024
        group by grouping sets ((region), ())
        order by 1 nulls first
        """,
        [
            (None,),
            ('EAST',),
            ('NORTH',),
            ('SOUTH',),
        ],
    )

    _assert_rows(
        act,
        'SELECT DISTINCT must collapse duplicate grouping sets by visible output',
        """
        select distinct
            region
        from gs_sales
        where fiscal_year = 2024
          and region = 'NORTH'
        group by grouping sets ((region), (region))
        order by 1
        """,
        [
            ('NORTH',),
        ],
    )


@pytest.mark.version('>=6.0')
def test_26_composite_grouping_items_are_expanded_as_units(act: Action):
    _assert_rows(
        act,
        'ROLLUP with composite grouping item',
        """
        select
            cast(grouping_id(region, dept, product) as integer) as gid,
            cast(grouping(region) as integer) as g_region,
            cast(grouping(dept) as integer) as g_dept,
            cast(grouping(product) as integer) as g_product,
            region,
            dept,
            product,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region = 'NORTH'
        group by rollup(region, (dept, product))
        order by gid, region nulls first, dept nulls first, product nulls first
        """,
        [
            (0, 0, 0, 0, 'NORTH', 'HARDWARE', 'HAMMER', 20),
            (0, 0, 0, 0, 'NORTH', 'HARDWARE', 'SAW',    15),
            (0, 0, 0, 0, 'NORTH', 'SOFTWARE', 'IDE',    60),
            (3, 0, 1, 1, 'NORTH', None,       None,     95),
            (7, 1, 1, 1, None,    None,       None,     95),
        ],
    )


@pytest.mark.version('>=6.0')
def test_27_window_function_in_same_select_as_grouping_sets(act: Action):
    _assert_rows(
        act,
        'window function in the same SELECT as GROUPING SETS',
        """
        select
            region,
            cast(sum(amount) as integer) as amount_sum,
            cast(row_number() over (order by sum(amount) desc, region nulls first) as integer) as rn
        from gs_sales
        where fiscal_year = 2024
          and region is not null
        group by grouping sets ((region), ())
        order by rn
        """,
        [
            (None, 220, 1),
            ('NORTH', 95, 2),
            ('SOUTH', 90, 3),
            ('EAST', 35, 4),
        ],
    )


@pytest.mark.version('>=6.0')
def test_28_rollup_nested_inside_grouping_sets(act: Action):
    _assert_rows(
        act,
        'ROLLUP nested inside GROUPING SETS',
        """
        select
            cast(grouping_id(region, dept, product) as integer) as gid,
            cast(grouping(region) as integer) as g_region,
            cast(grouping(dept) as integer) as g_dept,
            cast(grouping(product) as integer) as g_product,
            region,
            dept,
            product,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region = 'NORTH'
        group by grouping sets ((region), rollup(dept, product))
        order by gid, region nulls first, dept nulls first, product nulls first
        """,
        [
            (3, 0, 1, 1, 'NORTH', None,       None,     95),
            (4, 1, 0, 0, None,    'HARDWARE', 'HAMMER', 20),
            (4, 1, 0, 0, None,    'HARDWARE', 'SAW',    15),
            (4, 1, 0, 0, None,    'SOFTWARE', 'IDE',    60),
            (5, 1, 0, 1, None,    'HARDWARE', None,     35),
            (5, 1, 0, 1, None,    'SOFTWARE', None,     60),
            (7, 1, 1, 1, None,    None,       None,     95),
        ],
    )


@pytest.mark.version('>=6.0')
def test_29_multiargument_grouping_function(act: Action):
    _assert_rows(
        act,
        'multiargument GROUPING bit mask matches GROUPING_ID',
        """
        select
            cast(grouping(region, dept) as integer) as grouping_mask,
            cast(grouping_id(region, dept) as integer) as grouping_id_mask,
            cast(grouping(region) as integer) as g_region,
            cast(grouping(dept) as integer) as g_dept,
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
        group by cube(region, dept)
        order by grouping_mask, region nulls first, dept nulls first
        """,
        [
            (0, 0, 0, 0, None,    'HARDWARE',  12),
            (0, 0, 0, 0, 'EAST',  None,        10),
            (0, 0, 0, 0, 'EAST',  'HARDWARE',  25),
            (0, 0, 0, 0, 'NORTH', 'HARDWARE',  35),
            (0, 0, 0, 0, 'NORTH', 'SOFTWARE',  60),
            (0, 0, 0, 0, 'SOUTH', 'HARDWARE',  40),
            (0, 0, 0, 0, 'SOUTH', 'SOFTWARE',  50),
            (1, 1, 0, 1, None,    None,        12),
            (1, 1, 0, 1, 'EAST',  None,        35),
            (1, 1, 0, 1, 'NORTH', None,        95),
            (1, 1, 0, 1, 'SOUTH', None,        90),
            (2, 2, 1, 0, None,    None,        10),
            (2, 2, 1, 0, None,    'HARDWARE', 112),
            (2, 2, 1, 0, None,    'SOFTWARE', 110),
            (3, 3, 1, 1, None,    None,       232),
        ],
    )

    _assert_rows(
        act,
        'multiargument GROUPING in HAVING and ORDER BY',
        """
        select
            region,
            dept,
            cast(sum(amount) as integer) as amount_sum
        from gs_sales
        where fiscal_year = 2024
          and region is not null
        group by cube(region, dept)
        having grouping(region, dept) in (1, 3)
        order by grouping(region, dept), region nulls first
        """,
        [
            ('EAST',  None,  35),
            ('NORTH', None,  95),
            ('SOUTH', None,  90),
            (None,    None, 220),
        ],
    )


@pytest.mark.version('>=6.0')
def test_30_rollup_with_case_and_iif_expressions(act: Action):
    _assert_rows(
        act,
        'ROLLUP over CASE and IIF expressions',
        """
        select
            cast(grouping_id(
                cast(case
                    when region in ('NORTH', 'EAST') then 'NE'
                    when region is null then 'UNKNOWN'
                    else 'OTHER'
                end as varchar(10)),
                cast(iif(qty >= 3, 'BULK', 'SINGLE') as varchar(10))
            ) as integer) as gid,
            cast(grouping(
                cast(case
                    when region in ('NORTH', 'EAST') then 'NE'
                    when region is null then 'UNKNOWN'
                    else 'OTHER'
                end as varchar(10))
            ) as integer) as g_area,
            cast(grouping(cast(iif(qty >= 3, 'BULK', 'SINGLE') as varchar(10))) as integer) as g_qty,
            cast(case
                when region in ('NORTH', 'EAST') then 'NE'
                when region is null then 'UNKNOWN'
                else 'OTHER'
            end as varchar(10)) as area_bucket,
            cast(iif(qty >= 3, 'BULK', 'SINGLE') as varchar(10)) as qty_bucket,
            cast(sum(amount) as integer) as amount_sum,
            cast(count(*) as integer) as row_counts
        from gs_sales
        where fiscal_year = 2024
        group by rollup(
            cast(case
                when region in ('NORTH', 'EAST') then 'NE'
                when region is null then 'UNKNOWN'
                else 'OTHER'
            end as varchar(10)),
            cast(iif(qty >= 3, 'BULK', 'SINGLE') as varchar(10))
        )
        order by gid, area_bucket nulls first, qty_bucket nulls first
        """,
        [
            (0, 0, 0, 'NE     ', 'BULK  ',  85, 2),
            (0, 0, 0, 'NE     ', 'SINGLE',  45, 3),
            (0, 0, 0, 'OTHER  ', 'BULK  ',  40, 1),
            (0, 0, 0, 'OTHER  ', 'SINGLE',  50, 1),
            (0, 0, 0, 'UNKNOWN', 'SINGLE',  12, 1),
            (1, 0, 1, 'NE     ', None,     130, 5),
            (1, 0, 1, 'OTHER  ', None,      90, 2),
            (1, 0, 1, 'UNKNOWN', None,      12, 1),
            (3, 1, 1, None,      None,     232, 8),
        ],
    )


@pytest.mark.version('>=6.0')
def test_31_grouping_sets_with_string_and_date_expressions(act: Action):
    _assert_rows(
        act,
        'GROUPING SETS over EXTRACT, COALESCE, concatenation and SUBSTRING',
        """
        select
            cast(grouping_id(
                extract(year from sold_at),
                coalesce(region, 'NO_REGION') || ':' || substring(product from 1 for 1)
            ) as integer) as gid,
            cast(grouping(extract(year from sold_at)) as integer) as g_year,
            cast(grouping(
                coalesce(region, 'NO_REGION') || ':' || substring(product from 1 for 1)
            ) as integer) as g_key,
            cast(extract(year from sold_at) as integer) as sold_year,
            coalesce(region, 'NO_REGION') || ':' || substring(product from 1 for 1) as region_product_key,
            cast(sum(amount) as integer) as amount_sum
        from gs_regression_sales
        group by grouping sets (
            (
                extract(year from sold_at),
                coalesce(region, 'NO_REGION') || ':' || substring(product from 1 for 1)
            ),
            (extract(year from sold_at)),
            (coalesce(region, 'NO_REGION') || ':' || substring(product from 1 for 1)),
            ()
        )
        order by gid, sold_year nulls first, region_product_key nulls first
        """,
        [
            (0, 0, 0, 2024, 'NORTH:H', 20),
            (0, 0, 0, 2024, 'NORTH:I', 60),
            (0, 0, 0, 2024, 'NORTH:S', 15),
            (0, 0, 0, 2024, 'SOUTH:H', 40),
            (0, 0, 0, 2025, 'EAST:S',  25),
            (0, 0, 0, 2025, 'SOUTH:I', 30),
            (1, 0, 1, 2024, None,     135),
            (1, 0, 1, 2025, None,      55),
            (2, 1, 0, None, 'EAST:S',  25),
            (2, 1, 0, None, 'NORTH:H', 20),
            (2, 1, 0, None, 'NORTH:I', 60),
            (2, 1, 0, None, 'NORTH:S', 15),
            (2, 1, 0, None, 'SOUTH:H', 40),
            (2, 1, 0, None, 'SOUTH:I', 30),
            (3, 1, 1, None, None,     190),
        ],
    )


@pytest.mark.version('>=6.0')
def test_32_cube_with_nested_case_coalesce_and_upper_expressions(act: Action):
    _assert_rows(
        act,
        'CUBE over nested CASE, COALESCE and UPPER expressions',
        """
        select
            cast(grouping(
                cast(case when amount >= 40 then 'HIGH' else 'LOW' end as varchar(10)),
                upper(coalesce(dept, 'NO_DEPT'))
            ) as integer) as grouping_mask,
            cast(case when amount >= 40 then 'HIGH' else 'LOW' end as varchar(10)) as amount_band,
            upper(coalesce(dept, 'NO_DEPT')) as dept_key,
            cast(sum(amount) as integer) as amount_sum,
            cast(count(*) as integer) as row_counts
        from gs_sales
        where fiscal_year = 2024
        group by cube(
            cast(case when amount >= 40 then 'HIGH' else 'LOW' end as varchar(10)),
            upper(coalesce(dept, 'NO_DEPT'))
        )
        having grouping(
            cast(case when amount >= 40 then 'HIGH' else 'LOW' end as varchar(10)),
            upper(coalesce(dept, 'NO_DEPT'))
        ) <> 3
        order by grouping_mask, amount_band nulls first, dept_key nulls first
        """,
        [
            (0, 'HIGH', 'HARDWARE',  40, 1),
            (0, 'HIGH', 'SOFTWARE', 110, 2),
            (0, 'LOW ', 'HARDWARE',  72, 4),
            (0, 'LOW ', 'NO_DEPT',   10, 1),
            (1, 'HIGH', None,       150, 3),
            (1, 'LOW ', None,        82, 5),
            (2, None,   'HARDWARE', 112, 5),
            (2, None,   'NO_DEPT',   10, 1),
            (2, None,   'SOFTWARE', 110, 2),
        ],
    )


@pytest.mark.version('>=6.0')
def test_33_union_all_with_grouping_sets_and_ordinary_group_by(act: Action):
    _assert_rows(
        act,
        'UNION ALL combining grouping sets and ordinary GROUP BY',
        """
        select kind, g_region, region, amount_sum
        from (
            select
                'GS' as kind,
                cast(grouping(region) as integer) as g_region,
                region,
                cast(sum(amount) as integer) as amount_sum
            from gs_sales
            where fiscal_year = 2024
              and region in ('NORTH', 'SOUTH')
            group by grouping sets ((region), ())

            union all

            select
                'GB' as kind,
                0 as g_region,
                region,
                cast(sum(amount) as integer) as amount_sum
            from gs_sales
            where fiscal_year = 2024
              and region in ('NORTH', 'SOUTH')
            group by region
        ) u
        order by kind, g_region, region nulls first, amount_sum
        """,
        [
            ('GB', 0, 'NORTH',  95),
            ('GB', 0, 'SOUTH',  90),
            ('GS', 0, 'NORTH',  95),
            ('GS', 0, 'SOUTH',  90),
            ('GS', 1, None,    185),
        ],
    )


@pytest.mark.version('>=6.0')
def test_34_union_distinct_between_two_grouping_sets_queries(act: Action):
    _assert_rows(
        act,
        'UNION DISTINCT over two grouping sets queries removes duplicates',
        """
        select g_region, region, amount_sum
        from (
            select
                cast(grouping(region) as integer) as g_region,
                region,
                cast(sum(amount) as integer) as amount_sum
            from gs_sales
            where fiscal_year = 2024
              and region in ('NORTH', 'SOUTH')
            group by grouping sets ((region), ())

            union

            select
                cast(grouping(region) as integer) as g_region,
                region,
                cast(sum(amount) as integer) as amount_sum
            from gs_sales
            where fiscal_year = 2024
              and region in ('NORTH', 'SOUTH')
            group by rollup(region)
        ) u
        order by g_region, region nulls first
        """,
        [
            (0, 'NORTH',  95),
            (0, 'SOUTH',  90),
            (1, None,    185),
        ],
    )


@pytest.mark.version('>=6.0')
def test_35_nested_union_all_with_grouping_sets_rollup_and_plain_group_by(act: Action):
    _assert_rows(
        act,
        'nested UNION ALL with grouping sets, rollup and plain group by',
        """
        select src, gid, region, dept, amount_sum
        from (
            select
                'A' as src,
                cast(grouping_id(region, dept) as integer) as gid,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum
            from gs_sales
            where fiscal_year = 2024
              and region = 'NORTH'
            group by grouping sets ((region, dept), (region))

            union all

            select
                'B' as src,
                cast(grouping_id(region, dept) as integer) as gid,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum
            from gs_sales
            where fiscal_year = 2024
              and region = 'SOUTH'
            group by rollup(region, dept)

            union all

            select
                'C' as src,
                0 as gid,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum
            from gs_sales
            where fiscal_year = 2024
              and region = 'EAST'
            group by region, dept
        ) u
        order by src, gid, region nulls first, dept nulls first
        """,
        [
            ('A', 0, 'NORTH', 'HARDWARE', 35),
            ('A', 0, 'NORTH', 'SOFTWARE', 60),
            ('A', 1, 'NORTH', None,       95),
            ('B', 0, 'SOUTH', 'HARDWARE', 40),
            ('B', 0, 'SOUTH', 'SOFTWARE', 50),
            ('B', 1, 'SOUTH', None,       90),
            ('B', 3, None,    None,       90),
            ('C', 0, 'EAST',  None,       10),
            ('C', 0, 'EAST',  'HARDWARE', 25),
        ],
    )


@pytest.mark.version('>=6.0')
def test_36_named_window_in_same_select_as_rollup(act: Action):
    _assert_rows(
        act,
        'named window in the same SELECT as ROLLUP',
        """
        select
            region,
            cast(sum(amount) as integer) as amount_sum,
            cast(row_number() over w as integer) as rn
        from gs_sales
        where fiscal_year = 2024
          and region is not null
        group by rollup(region)
        window w as (order by sum(amount) desc, region nulls first)
        order by rn
        """,
        [
            (None, 220, 1),
            ('NORTH', 95, 2),
            ('SOUTH', 90, 3),
            ('EAST', 35, 4),
        ],
    )


@pytest.mark.version('>=6.0')
def test_37_window_order_uses_hidden_aggregate_dependency(act: Action):
    _assert_rows(
        act,
        'window ORDER BY uses aggregate not present in the select list',
        """
        select
            region,
            cast(row_number() over (order by sum(amount) desc, region nulls first) as integer) as rn
        from gs_sales
        where fiscal_year = 2024
          and region is not null
        group by grouping sets ((region), ())
        order by rn
        """,
        [
            (None, 1),
            ('NORTH', 2),
            ('SOUTH', 3),
            ('EAST', 4),
        ],
    )


@pytest.mark.version('>=6.0')
def test_38_window_grouping_sets_union_all_and_cte(act: Action):
    _assert_rows(
        act,
        'window functions with grouping sets, rollup, union all and CTEs',
        """
        with base_sales as (
            select region, dept, amount
            from gs_sales
            where fiscal_year = 2024
              and region is not null
        ),
        combined as (
            select
                cast('GS' as varchar(4)) as src,
                cast(grouping_id(region, dept) as integer) as gid,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum,
                cast(row_number() over (
                    partition by grouping_id(region, dept)
                    order by sum(amount) desc, region nulls first, dept nulls first
                ) as integer) as branch_rn
            from base_sales
            group by grouping sets ((region, dept), (region), ())

            union all

            select
                cast('ROLL' as varchar(4)) as src,
                cast(grouping_id(region, dept) as integer) as gid,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum,
                cast(row_number() over (
                    partition by grouping_id(region, dept)
                    order by sum(amount) desc, region nulls first, dept nulls first
                ) as integer) as branch_rn
            from base_sales
            where region in ('NORTH', 'SOUTH')
            group by rollup(region, dept)
        ),
        ranked as (
            select
                src,
                gid,
                region,
                dept,
                amount_sum,
                branch_rn,
                cast(sum(amount_sum) over (
                    partition by src
                    order by gid, branch_rn, region nulls first, dept nulls first
                    rows between unbounded preceding and current row
                ) as integer) as running_amount
            from combined
        )
        select src, gid, region, dept, amount_sum, branch_rn, running_amount
        from ranked
        where gid <> 0
           or branch_rn <= 3
        order by src, gid, branch_rn, region nulls first, dept nulls first
        """,
        [
            ('GS',   0, 'NORTH', 'SOFTWARE',  60, 1,  60),
            ('GS',   0, 'SOUTH', 'SOFTWARE',  50, 2, 110),
            ('GS',   0, 'SOUTH', 'HARDWARE',  40, 3, 150),
            ('GS',   1, 'NORTH', None,        95, 1, 315),
            ('GS',   1, 'SOUTH', None,        90, 2, 405),
            ('GS',   1, 'EAST',  None,        35, 3, 440),
            ('GS',   3, None,    None,       220, 1, 660),
            ('ROLL', 0, 'NORTH', 'SOFTWARE',  60, 1,  60),
            ('ROLL', 0, 'SOUTH', 'SOFTWARE',  50, 2, 110),
            ('ROLL', 0, 'SOUTH', 'HARDWARE',  40, 3, 150),
            ('ROLL', 1, 'NORTH', None,        95, 1, 280),
            ('ROLL', 1, 'SOUTH', None,        90, 2, 370),
            ('ROLL', 3, None,    None,       185, 1, 555),
        ],
    )


@pytest.mark.version('>=6.0')
def test_39_grouping_functions_inside_window_partition_clause(act: Action):
    _assert_rows(
        act,
        'GROUPING and GROUPING_ID inside a window partition clause',
        """
        with grouped as (
            select
                cast(grouping_id(region, dept) as integer) as gid,
                cast(grouping(region) as integer) as g_region,
                region,
                dept,
                cast(sum(amount) as integer) as amount_sum,
                cast(row_number() over (
                    partition by grouping(region), grouping_id(region, dept)
                    order by sum(amount) desc, region nulls first, dept nulls first
                ) as integer) as rn_in_bucket
            from gs_sales
            where fiscal_year = 2024
              and region is not null
            group by grouping sets ((region, dept), (region), ())
        ),
        filtered as (
            select *
            from grouped
            where gid <> 0
               or rn_in_bucket <= 2
        ),
        ranked as (
            select
                gid,
                g_region,
                region,
                dept,
                amount_sum,
                rn_in_bucket,
                cast(count(*) over (partition by gid) as integer) as rows_in_gid,
                cast(sum(amount_sum) over (
                    order by gid, rn_in_bucket, region nulls first, dept nulls first
                    rows between unbounded preceding and current row
                ) as integer) as running_amount
            from filtered
        )
        select
            gid,
            g_region,
            region,
            dept,
            amount_sum,
            rn_in_bucket,
            rows_in_gid,
            running_amount
        from ranked
        order by gid, rn_in_bucket, region nulls first, dept nulls first
        """,
        [
            (0, 0, 'NORTH', 'SOFTWARE',  60, 1, 2,  60),
            (0, 0, 'SOUTH', 'SOFTWARE',  50, 2, 2, 110),
            (1, 0, 'NORTH', None,        95, 1, 3, 205),
            (1, 0, 'SOUTH', None,        90, 2, 3, 295),
            (1, 0, 'EAST',  None,        35, 3, 3, 330),
            (3, 1, None,    None,       220, 1, 1, 550),
        ],
    )
