#coding:utf-8

"""
ID:          issue-9183
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9183
TITLE:       Regressions in FB 5.x when boolean-as-value expression is used and OuterJoinConversion = true
DESCRIPTION:
    Test uses list of queries that were detected by SQLancer as problematic when Ternary Logic Partitioning
    is applied to check correctness of their results -- see 'QRY_LIST'.
    All pairs of queries must produce same results (regardless on rows order).
    Otherwise result is considered as unexpected and DDL, DML + both queries are shown.
NOTES:
    [28.11.2026] pzotov
    Custom driver config object is used ('OuterJoinConversion = true' must be explicitly set for FB 5.x).
    Confirmed bug on 6.0.0.2514-ec98b74 ; 5.0.5.1993-e8a9ef1
    Checked on 6.0.0.2516-1982b96 ; 5.0.5.1994-bd900ec ; 4.0.8.3340-56f03d5.
"""

from collections import Counter
import pytest
from firebird.qa import *
from firebird.driver import DatabaseError, driver_config, connect

db = db_factory()
act = python_act('db')

EXPECTED_MSG = 'OK: no mismatches found.'
@pytest.mark.version('>=4.0')
def test_1(act: Action, capsys):

    # QRY_LIST = list of tuples, every tuple has three elements with indices:
    #   idx-0: multi-line string with DDL statements, delimited by `;`
    #   idx-1: multi-line string with INSERTS, delimited by `;`
    #   idx-2: initial query to be checked further by Ternary Logic Partitioning;
    #   idx-3: query that is sued to check initial (specified in idx-2)
    QRY_LIST = [
        # ==================== database1 ====================
        (

            """
                create table t_01_69(f_01_69_00 char(8));
                create table t_01_00(f_01_00_00 varchar(20) unique);
                create index i_01_00 on t_01_69(f_01_69_00);
                create index i_01_01 on t_01_00(f_01_00_00);
            """
            ,
            """
                insert into t_01_69(f_01_69_00) values ('');
                insert into t_01_00(f_01_00_00) values ('');
                insert into t_01_00(f_01_00_00) values ('be');
                insert into t_01_00(f_01_00_00) values ('cbdaee');
                insert into t_01_00(f_01_00_00) values ('ef');
            """
            ,
            """
                select t_01_69.f_01_69_00
                from t_01_00
                right join t_01_69 on
                    (
                        cast(279 as bigint) in (1130)
                        and
                        cast(null as boolean)
                    )
            """
            ,
            """
                select t_01_69.f_01_69_00
                from t_01_00
                right join t_01_69 on
                    (
                        cast(279 as bigint) in (1130)
                        and
                        cast(null as boolean)
                    )
                where (
                        (
                                false
                                and
                                t_01_00.f_01_00_00 between t_01_00.f_01_00_00 and t_01_00.f_01_00_00
                            ) <> true
                      )
                UNION ALL
                select t_01_69.f_01_69_00
                from t_01_00
                right join t_01_69 on
                    (
                        cast(279 as bigint) in (1130)
                        and
                        cast(null as boolean)
                    )
                where (
                        not (
                                (
                                        false
                                        and
                                        t_01_00.f_01_00_00 between t_01_00.f_01_00_00 and t_01_00.f_01_00_00
                                    ) <> true
                            )
                      )
                UNION ALL
                select t_01_69.f_01_69_00
                from t_01_00
                right join t_01_69 on
                    (
                        cast(279 as bigint) in (1130)
                        and
                        cast(null as boolean)
                    )
                where (
                        (
                                (
                                        false
                                        and
                                        t_01_00.f_01_00_00 between t_01_00.f_01_00_00 and t_01_00.f_01_00_00
                                    ) <> true
                            ) is null
                      )

            """
        )
        ,

        # ==================== database2 ====================
        (
            """
                create table t_02_00(f_02_00_00 smallint, f_02_00_01 bigint, f_02_00_02 date, primary key(f_02_00_00));
                create table t_02_01(f_02_01_00 varchar(20));
                create index i_02_00 on t_02_01(f_02_01_00);
                create index i_02_99 on t_02_01(f_02_01_00);
            """
            ,
            """
                insert into t_02_01(f_02_01_00) values ('');
                insert into t_02_01(f_02_01_00) values ('');
            """
            ,
            """
                select t_02_00.f_02_00_00
                from t_02_00
                right join t_02_01 on
                    (
                        true
                        or
                        true
                    )
            """
            ,
            """
                select t_02_00.f_02_00_00
                from t_02_00
                right join t_02_01 on
                    (
                        true
                        or
                        true
                    )
                where (
                        true between
                            (
                                    t_02_00.f_02_00_01 * t_02_00.f_02_00_01 between
                                        cast(-3645 as bigint)
                                        and
                                        t_02_00.f_02_00_01
                            )
                            and
                            (
                                    false
                                    and
                                    t_02_00.f_02_00_02 <> t_02_00.f_02_00_02
                            )
                      )
                UNION ALL
                select t_02_00.f_02_00_00
                from t_02_00
                right join t_02_01 on
                    (
                        true
                        or
                        true
                    )
                where (
                        not (
                                true between
                                    (
                                            t_02_00.f_02_00_01 * t_02_00.f_02_00_01 between
                                                cast(-3645 as bigint)
                                                and
                                                t_02_00.f_02_00_01
                                    )
                                    and
                                    (
                                            false
                                            and
                                            t_02_00.f_02_00_02 <> t_02_00.f_02_00_02
                                    )
                            )
                      )
                UNION ALL
                select t_02_00.f_02_00_00
                from t_02_00
                right join t_02_01 on
                    (
                        true
                        or
                        true
                    )
                where (
                        (
                                true between
                                    (
                                            t_02_00.f_02_00_01 * t_02_00.f_02_00_01 between
                                                cast(-3645 as bigint)
                                                and
                                                t_02_00.f_02_00_01
                                    )
                                    and
                                    (
                                            false
                                            and
                                            t_02_00.f_02_00_02 <> t_02_00.f_02_00_02
                                    )
                            ) is null
                      )
                ;

            """
        )
        ,
        # ==================== database3 ====================
        (
            """
                create table t_03_00(f_03_00_00 char(8) not null unique, f_03_00_01 date, f_03_00_02 boolean unique);
                create table t_03_01(f_03_01_00 date, f_03_01_01 varchar(20), f_03_01_02 varchar(20));
            """
            ,
            """
                insert into t_03_01(f_03_01_00, f_03_01_01, f_03_01_02) values (null, 'dc', null);
            """
            ,
            """
                select t_03_01.f_03_01_00
                from t_03_01
                left join t_03_00 on
                    (
                        t_03_00.f_03_00_02
                        or
                        not t_03_00.f_03_00_02
                    )
            """
            ,
            """
                select t_03_01.f_03_01_00
                from t_03_01
                left join t_03_00 on
                    (
                        t_03_00.f_03_00_02
                        or
                        not t_03_00.f_03_00_02
                    )
                where (
                        (
                                false
                                and
                                t_03_00.f_03_00_02 in (t_03_00.f_03_00_02, t_03_00.f_03_00_02, t_03_00.f_03_00_02)
                            ) between
                            (t_03_01.f_03_01_00 is null)
                            and
                            t_03_00.f_03_00_02
                      )
                UNION ALL
                select t_03_01.f_03_01_00
                from t_03_01
                left join t_03_00 on
                    (
                        t_03_00.f_03_00_02
                        or
                        not t_03_00.f_03_00_02
                    )
                where (
                        not (
                                (
                                        false
                                        and
                                        t_03_00.f_03_00_02 in (t_03_00.f_03_00_02, t_03_00.f_03_00_02, t_03_00.f_03_00_02)
                                    ) between
                                    (t_03_01.f_03_01_00 is null)
                                    and
                                    t_03_00.f_03_00_02
                            )
                      )
                UNION ALL
                select t_03_01.f_03_01_00
                from t_03_01
                left join t_03_00 on
                    (
                        t_03_00.f_03_00_02
                        or
                        not t_03_00.f_03_00_02
                    )
                where (
                        (
                                (
                                        false
                                        and
                                        t_03_00.f_03_00_02 in (t_03_00.f_03_00_02, t_03_00.f_03_00_02, t_03_00.f_03_00_02)
                                    ) between
                                    (t_03_01.f_03_01_00 is null)
                                    and
                                    t_03_00.f_03_00_02
                            ) is null
                      )
            """
        )
        ,
        # ==================== database4 ====================
        (
            """
                create table t_04_00(f_04_00_00 date unique);
                create view v_04_00 as select t_04_00.f_04_00_00 from t_04_00;
            """
            ,
            """
                insert into t_04_00(f_04_00_00) values (null);
                insert into t_04_00(f_04_00_00) values (null);
                insert into t_04_00(f_04_00_00) values (null);
                insert into t_04_00(f_04_00_00) values (null);
                insert into t_04_00(f_04_00_00) values (null);
                insert into t_04_00(f_04_00_00) values (date '1970-01-01');
                insert into t_04_00(f_04_00_00) values (date '2000-01-01');
                insert into t_04_00(f_04_00_00) values (date '2020-02-29');
            """
            ,
            """
                select v_04_00.f_04_00_00
                from t_04_00
                left join v_04_00 on
                    t_04_00.f_04_00_00 > v_04_00.f_04_00_00
            """
            ,
            """
                select v_04_00.f_04_00_00
                from t_04_00
                left join v_04_00 on
                    t_04_00.f_04_00_00 > v_04_00.f_04_00_00
                where (
                        (t_04_00.f_04_00_00 between date '2020-02-29' and v_04_00.f_04_00_00) in (
                            false,
                            cast(null as boolean),
                            (0.74 in (0.43, cast(null as double precision), 0.21)),
                            false,
                            true
                        )
                      )
                UNION ALL
                select v_04_00.f_04_00_00
                from t_04_00
                left join v_04_00 on
                    t_04_00.f_04_00_00 > v_04_00.f_04_00_00
                where (
                        not (
                                (t_04_00.f_04_00_00 between date '2020-02-29' and v_04_00.f_04_00_00) in (
                                    false,
                                    cast(null as boolean),
                                    (0.74 in (0.43, cast(null as double precision), 0.21)),
                                    false,
                                    true
                                )
                            )
                      )
                UNION ALL
                select v_04_00.f_04_00_00
                from t_04_00
                left join v_04_00 on
                    t_04_00.f_04_00_00 > v_04_00.f_04_00_00
                where (
                        (
                                (t_04_00.f_04_00_00 between date '2020-02-29' and v_04_00.f_04_00_00) in (
                                    false,
                                    cast(null as boolean),
                                    (0.74 in (0.43, cast(null as double precision), 0.21)),
                                    false,
                                    true
                                )
                            ) is null
                      )
            """
        )
        ,
        # ==================== database5 ====================
        (
            """
                create table t_05_00(f_05_00_00 boolean, f_05_00_01 boolean unique, f_05_00_02 integer, primary key(f_05_00_02));
                create table t_05_19(f_05_19_00 boolean, f_05_19_01 bigint, f_05_19_02 char(8));
                create view v_05_00 as select t_05_00.f_05_00_02, t_05_00.f_05_00_00, t_05_00.f_05_00_01 from t_05_00;
            """
            ,
            """
                insert into t_05_00(f_05_00_00, f_05_00_01, f_05_00_02) values (null, null, -8407);
                insert into t_05_00(f_05_00_00, f_05_00_01, f_05_00_02) values (null, TRUE, 2361);
                insert into t_05_19(f_05_19_00, f_05_19_01, f_05_19_02) values (FALSE, 6271, '');
            """
            ,
            """
                select t_05_19.f_05_19_01
                from t_05_19
                left join v_05_00 on
                    false
            """
            ,
            """
                select t_05_19.f_05_19_01
                from t_05_19
                left join v_05_00 on
                    false
                where (
                        (v_05_00.f_05_00_02 is null) >= (
                                0.71 is null
                                and
                                not v_05_00.f_05_00_01
                            )
                      )
                UNION ALL
                select t_05_19.f_05_19_01
                from t_05_19
                left join v_05_00 on
                    false
                where (
                        not (
                                (v_05_00.f_05_00_02 is null) >= (
                                        0.71 is null
                                        and
                                        not v_05_00.f_05_00_01
                                    )
                            )
                      )
                UNION ALL
                select t_05_19.f_05_19_01
                from t_05_19
                left join v_05_00 on
                    false
                where (
                        (
                                (v_05_00.f_05_00_02 is null) >= (
                                        0.71 is null
                                        and
                                        not v_05_00.f_05_00_01
                                    )
                            ) is null
                      )
            """
        )
        ,
        # ==================== database7 ====================
        (
            """
                create table t_07_00(f_07_00_00 date, f_07_00_01 boolean, f_07_00_02 double precision);
                create view v_07_00 as select t_07_00.f_07_00_01 from t_07_00;
                create index i_07_00 on t_07_00(f_07_00_02);
            """
            ,
            """
                insert into t_07_00(f_07_00_00, f_07_00_01, f_07_00_02) values (null, TRUE, null);
                insert into t_07_00(f_07_00_00, f_07_00_01, f_07_00_02) values (date '2020-02-29', null, null);
                insert into t_07_00(f_07_00_00, f_07_00_01, f_07_00_02) values (date '2020-02-29', null, 0.7500000000000000);
                insert into t_07_00(f_07_00_00, f_07_00_01, f_07_00_02) values (date '2020-02-29', FALSE, null);
                insert into t_07_00(f_07_00_00, f_07_00_01, f_07_00_02) values (date '2020-02-29', TRUE, 0.1600000000000000);
                insert into t_07_00(f_07_00_00, f_07_00_01, f_07_00_02) values (date '2020-02-29', TRUE, 0.2400000000000000);
            """
            ,
            """
                select t_07_00.f_07_00_00
                from v_07_00
                right join t_07_00 on
                    abs(-2066) is null
            """
            ,
            """
                select t_07_00.f_07_00_00
                from v_07_00
                right join t_07_00 on
                    abs(-2066) is null
                where (
                        (
                                t_07_00.f_07_00_01
                                and
                                not v_07_00.f_07_00_01
                            ) <= t_07_00.f_07_00_01
                      )
                UNION ALL
                select t_07_00.f_07_00_00
                from v_07_00
                right join t_07_00 on
                    abs(-2066) is null
                where (
                        not (
                                (
                                        t_07_00.f_07_00_01
                                        and
                                        not v_07_00.f_07_00_01
                                    ) <= t_07_00.f_07_00_01
                            )
                      )
                UNION ALL
                select t_07_00.f_07_00_00
                from v_07_00
                right join t_07_00 on
                    abs(-2066) is null
                where (
                        (
                                (
                                        t_07_00.f_07_00_01
                                        and
                                        not v_07_00.f_07_00_01
                                    ) <= t_07_00.f_07_00_01
                            ) is null
                      )
            """
        )
        ,
        # ==================== database8 ====================
        (
            """
                create table t_08_00(f_08_00_00 varchar(20), f_08_00_01 varchar(20), f_08_00_02 double precision);
                create table t_08_01(f_08_01_00 smallint not null, f_08_01_01 smallint unique, f_08_01_02 date);
                create unique index i_08_00 on t_08_00(f_08_00_00);
                create unique index i_08_01 on t_08_01(f_08_01_01);
            """
            ,
            """
                insert into t_08_00(f_08_00_00, f_08_00_01, f_08_00_02) values (null, null, 0.5400000000000000);
                insert into t_08_00(f_08_00_00, f_08_00_01, f_08_00_02) values (null, null, 0.1800000000000000);
                insert into t_08_00(f_08_00_00, f_08_00_01, f_08_00_02) values ('', '', 0.4900000000000000);
            """
            ,
            """
                select t_08_01.f_08_01_02
                from t_08_00
                left join t_08_01 on
                    true
            """
            ,
            """
                select t_08_01.f_08_01_02
                from t_08_00
                left join t_08_01 on
                    true
                where (
                        (
                                t_08_01.f_08_01_02 between t_08_01.f_08_01_02 and cast(null as date)
                                and
                                not true
                            ) in (
                            (time '12:34:56' is null)
                        )
                      )
                UNION ALL
                select t_08_01.f_08_01_02
                from t_08_00
                left join t_08_01 on
                    true
                where (
                        not (
                                (
                                        t_08_01.f_08_01_02 between t_08_01.f_08_01_02 and cast(null as date)
                                        and
                                        not true
                                    ) in (
                                    (time '12:34:56' is null)
                                )
                            )
                      )
                UNION ALL
                select t_08_01.f_08_01_02
                from t_08_00
                left join t_08_01 on
                    true
                where (
                        (
                                (
                                        t_08_01.f_08_01_02 between t_08_01.f_08_01_02 and cast(null as date)
                                        and
                                        not true
                                    ) in (
                                    (time '12:34:56' is null)
                                )
                            ) is null
                      )
            """
        )
        ,
        # ==================== database9 ====================
        (
            """
                create table t_09_80(f_09_80_00 varchar(20), f_09_80_01 varchar(20), f_09_80_02 char(8), f_09_80_03 bigint, f_09_80_04 smallint);
                create unique index i_09_00 on t_09_80(f_09_80_02);
                create view v_09_00 as select t_09_80.f_09_80_02, t_09_80.f_09_80_01, t_09_80.f_09_80_00, t_09_80.f_09_80_03 from t_09_80;
            """
            ,
            """
                insert into t_09_80(f_09_80_00, f_09_80_01, f_09_80_02, f_09_80_03, f_09_80_04) values (null, '', null, null, null);
                insert into t_09_80(f_09_80_00, f_09_80_01, f_09_80_02, f_09_80_03, f_09_80_04) values (null, 'ed', null, null, null);
                insert into t_09_80(f_09_80_00, f_09_80_01, f_09_80_02, f_09_80_03, f_09_80_04) values ('af', null, null, null, null);
                insert into t_09_80(f_09_80_00, f_09_80_01, f_09_80_02, f_09_80_03, f_09_80_04) values (null, null, '', null, null);
            """
            ,
            """
                select v_09_00.f_09_80_02
                from t_09_80
                right join v_09_00 on
                    cast(null as boolean)
            """
            ,
            """
                select v_09_00.f_09_80_02
                from t_09_80
                right join v_09_00 on
                    cast(null as boolean)
                where (
                        (
                                t_09_80.f_09_80_03 <= t_09_80.f_09_80_03
                                and
                                false
                            ) = (not true)
                      )
                UNION ALL
                select v_09_00.f_09_80_02
                from t_09_80
                right join v_09_00 on
                    cast(null as boolean)
                where (
                        not (
                                (
                                        t_09_80.f_09_80_03 <= t_09_80.f_09_80_03
                                        and
                                        false
                                    ) = (not true)
                            )
                      )
                UNION ALL
                select v_09_00.f_09_80_02
                from t_09_80
                right join v_09_00 on
                    cast(null as boolean)
                where (
                        (
                                (
                                        t_09_80.f_09_80_03 <= t_09_80.f_09_80_03
                                        and
                                        false
                                    ) = (not true)
                            ) is null
                      )
            """
        )
        ,
        # ==================== database11 ====================
        (
            """
                create table t_11_00(f_11_00_00 boolean, f_11_00_01 numeric(9, 2), f_11_00_02 varchar(20));
                create table t_11_01(f_11_01_00 smallint, primary key(f_11_01_00));
                create unique index i_11_00 on t_11_01(f_11_01_00);
                create index i_11_01 on t_11_00(f_11_00_01);
            """
            ,
            """
                insert into t_11_01(f_11_01_00) values (63);
            """
            ,
            """
                select t_11_01.f_11_01_00
                from t_11_01
                left join t_11_00 on
                    0.88 is null
            """
            ,
            """
                select t_11_01.f_11_01_00
                from t_11_01
                left join t_11_00 on
                    0.88 is null
                where (
                        (date '2020-02-29' <= date '2020-02-29') < (
                                0.31 in (0.09)
                                and
                                t_11_00.f_11_00_00
                            )
                      )
                UNION ALL
                select t_11_01.f_11_01_00
                from t_11_01
                left join t_11_00 on
                    0.88 is null
                where (
                        not (
                                (date '2020-02-29' <= date '2020-02-29') < (
                                        0.31 in (0.09)
                                        and
                                        t_11_00.f_11_00_00
                                    )
                            )
                      )
                UNION ALL
                select t_11_01.f_11_01_00
                from t_11_01
                left join t_11_00 on
                    0.88 is null
                where (
                        (
                                (date '2020-02-29' <= date '2020-02-29') < (
                                        0.31 in (0.09)
                                        and
                                        t_11_00.f_11_00_00
                                    )
                            ) is null
                      )
            """
        )
        ,
        # ==================== database12 ====================
        (
            """
                create table t_12_00(f_12_00_00 boolean);
                create table t_12_01(f_12_01_00 time);
                create unique index i_12_00 on t_12_00(f_12_00_00);
                create view v_12_00 as select t_12_00.f_12_00_00 from t_12_00;
                create unique index i_12_01 on t_12_00(f_12_00_00);
            """
            ,
            """
                insert into t_12_00(f_12_00_00) values (null);
                insert into t_12_00(f_12_00_00) values (null);
                insert into t_12_00(f_12_00_00) values (FALSE);
                insert into t_12_00(f_12_00_00) values (TRUE);
                insert into t_12_01(f_12_01_00) values (null);
                insert into t_12_01(f_12_01_00) values (null);
                insert into t_12_01(f_12_01_00) values (null);
                insert into t_12_01(f_12_01_00) values (null);
                insert into t_12_01(f_12_01_00) values (null);
                insert into t_12_01(f_12_01_00) values (null);
                insert into t_12_01(f_12_01_00) values (null);
                insert into t_12_01(f_12_01_00) values (time '00:00:00.0000');
                insert into t_12_01(f_12_01_00) values (time '00:00:00.0000');
                insert into t_12_01(f_12_01_00) values (time '00:00:00.0000');
                insert into t_12_01(f_12_01_00) values (time '12:34:56.0000');
                insert into t_12_01(f_12_01_00) values (time '23:59:59.0000');
                insert into t_12_01(f_12_01_00) values (time '23:59:59.0000');
                insert into t_12_01(f_12_01_00) values (time '23:59:59.0000');
            """
            ,
            """
                select t_12_01.f_12_01_00
                from t_12_00
                left join t_12_01 on
                    t_12_00.f_12_00_00
                right join v_12_00 on
                    (
                        abs(8339) <> -4102
                        and
                        v_12_00.f_12_00_00
                    )
            """
            ,
            """
                select t_12_01.f_12_01_00
                from t_12_00
                left join t_12_01 on
                    t_12_00.f_12_00_00
                right join v_12_00 on
                    (
                        abs(8339) <> -4102
                        and
                        v_12_00.f_12_00_00
                    )
                where (
                        (
                                t_12_00.f_12_00_00
                                and
                                v_12_00.f_12_00_00
                            ) in (
                            (-9182 in (317))
                        )
                      )
                UNION ALL
                select t_12_01.f_12_01_00
                from t_12_00
                left join t_12_01 on
                    t_12_00.f_12_00_00
                right join v_12_00 on
                    (
                        abs(8339) <> -4102
                        and
                        v_12_00.f_12_00_00
                    )
                where (
                        not (
                                (
                                        t_12_00.f_12_00_00
                                        and
                                        v_12_00.f_12_00_00
                                    ) in (
                                    (-9182 in (317))
                                )
                            )
                      )
                UNION ALL
                select t_12_01.f_12_01_00
                from t_12_00
                left join t_12_01 on
                    t_12_00.f_12_00_00
                right join v_12_00 on
                    (
                        abs(8339) <> -4102
                        and
                        v_12_00.f_12_00_00
                    )
                where (
                        (
                                (
                                        t_12_00.f_12_00_00
                                        and
                                        v_12_00.f_12_00_00
                                    ) in (
                                    (-9182 in (317))
                                )
                            ) is null
                      )
            """
        )
        ,
        # ==================== database13 ====================
        (
            """
                create table t_13_00(f_13_00_00 integer, f_13_00_01 boolean, f_13_00_02 integer);
                create table t_13_01(f_13_01_00 float);
                create index i_13_00 on t_13_00(f_13_00_01);
            """
            ,
            """
                insert into t_13_00(f_13_00_00, f_13_00_01, f_13_00_02) values (null, null, 3120);
                insert into t_13_00(f_13_00_00, f_13_00_01, f_13_00_02) values (8105, null, 5514);
                insert into t_13_00(f_13_00_00, f_13_00_01, f_13_00_02) values (8105, null, 7132);
                insert into t_13_00(f_13_00_00, f_13_00_01, f_13_00_02) values (8105, FALSE, -6804);
                insert into t_13_01(f_13_01_00) values (null);
                insert into t_13_01(f_13_01_00) values (0.0000000);
                insert into t_13_01(f_13_01_00) values (0.25000000);
                insert into t_13_01(f_13_01_00) values (0.38999999);
                insert into t_13_01(f_13_01_00) values (0.50000000);
                insert into t_13_01(f_13_01_00) values (0.50000000);
                insert into t_13_01(f_13_01_00) values (0.57999998);
                insert into t_13_01(f_13_01_00) values (0.62000000);
                insert into t_13_01(f_13_01_00) values (0.62000000);
            """
            ,
            """
                select t_13_00.f_13_00_00
                from t_13_01
                left join t_13_00 on
                    t_13_00.f_13_00_01
            """
            ,
            """
                select t_13_00.f_13_00_00
                from t_13_01
                left join t_13_00 on
                    t_13_00.f_13_00_01
                where (
                        (
                                (
                                        t_13_00.f_13_00_01
                                        and
                                        true
                                    )
                                and
                                date '2000-01-01' = date '1970-01-01'
                            ) > (cast(null as timestamp) is null)
                      )
                UNION ALL
                select t_13_00.f_13_00_00
                from t_13_01
                left join t_13_00 on
                    t_13_00.f_13_00_01
                where (
                        not (
                                (
                                        (
                                                t_13_00.f_13_00_01
                                                and
                                                true
                                            )
                                        and
                                        date '2000-01-01' = date '1970-01-01'
                                    ) > (cast(null as timestamp) is null)
                            )
                      )
                UNION ALL
                select t_13_00.f_13_00_00
                from t_13_01
                left join t_13_00 on
                    t_13_00.f_13_00_01
                where (
                        (
                                (
                                        (
                                                t_13_00.f_13_00_01
                                                and
                                                true
                                            )
                                        and
                                        date '2000-01-01' = date '1970-01-01'
                                    ) > (cast(null as timestamp) is null)
                            ) is null
                      )
            """
        )
        ,
        # ==================== database16 ====================
        (
            """
                create table t_16_00(f_16_00_00 smallint unique, f_16_00_01 time unique, f_16_00_02 boolean);
                create unique index i_16_00 on t_16_00(f_16_00_02);
                create view v_16_00 as select t_16_00.f_16_00_02 from t_16_00;
            """
            ,
            """
                insert into t_16_00(f_16_00_00, f_16_00_01, f_16_00_02) values (null, null, null);
                insert into t_16_00(f_16_00_00, f_16_00_01, f_16_00_02) values (-632, time '00:00:00.0000', null);
                insert into t_16_00(f_16_00_00, f_16_00_01, f_16_00_02) values (179, time '12:34:56.0000', null);
                insert into t_16_00(f_16_00_00, f_16_00_01, f_16_00_02) values (630, null, null);
            """
            ,
            """
                select t_16_00.f_16_00_02
                from v_16_00
                left join t_16_00 on
                    (
                        not (
                                'af' is null
                                or
                                not t_16_00.f_16_00_02
                            )
                    )
            """
            ,
            """
                select t_16_00.f_16_00_02
                from v_16_00
                left join t_16_00 on
                    (
                        not (
                                'af' is null
                                or
                                not t_16_00.f_16_00_02
                            )
                    )
                where (
                        (
                                (
                                        date '1970-01-01' between
                                            date '2000-01-01'
                                            and
                                            date '1970-01-01'
                                    )
                                and
                                t_16_00.f_16_00_02
                            ) between
                            (cast(-1407 as integer) > -4155)
                            and
                            (
                                    t_16_00.f_16_00_02 >= false
                                    or
                                    t_16_00.f_16_00_02
                            )
                      )
                UNION ALL
                select t_16_00.f_16_00_02
                from v_16_00
                left join t_16_00 on
                    (
                        not (
                                'af' is null
                                or
                                not t_16_00.f_16_00_02
                            )
                    )
                where (
                        not (
                                (
                                        (
                                                date '1970-01-01' between
                                                    date '2000-01-01'
                                                    and
                                                    date '1970-01-01'
                                            )
                                        and
                                        t_16_00.f_16_00_02
                                    ) between
                                    (cast(-1407 as integer) > -4155)
                                    and
                                    (
                                            t_16_00.f_16_00_02 >= false
                                            or
                                            t_16_00.f_16_00_02
                                    )
                            )
                      )
                UNION ALL
                select t_16_00.f_16_00_02
                from v_16_00
                left join t_16_00 on
                    (
                        not (
                                'af' is null
                                or
                                not t_16_00.f_16_00_02
                            )
                    )
                where (
                        (
                                (
                                        (
                                                date '1970-01-01' between
                                                    date '2000-01-01'
                                                    and
                                                    date '1970-01-01'
                                            )
                                        and
                                        t_16_00.f_16_00_02
                                    ) between
                                    (cast(-1407 as integer) > -4155)
                                    and
                                    (
                                            t_16_00.f_16_00_02 >= false
                                            or
                                            t_16_00.f_16_00_02
                                    )
                            ) is null
                      )
            """
        )
        ,
        # ==================== database17 ====================
        (
            """
                create table t_17_00(f_17_00_00 date not null, f_17_00_01 varchar(20), f_17_00_02 bigint, primary key(f_17_00_02));
                create table t_17_01(f_17_01_00 boolean);
                create index i_17_00 on t_17_00(f_17_00_01);
                create view v_17_00 as select t_17_01.f_17_01_00 from t_17_01;
            """
            ,
            """
                insert into t_17_00(f_17_00_00, f_17_00_01, f_17_00_02) values (date '2020-02-29', '', 3946);
                insert into t_17_00(f_17_00_00, f_17_00_01, f_17_00_02) values (date '2020-02-29', '', 9361);
                insert into t_17_01(f_17_01_00) values (null);
                insert into t_17_01(f_17_01_00) values (FALSE);
                insert into t_17_01(f_17_01_00) values (FALSE);
                insert into t_17_01(f_17_01_00) values (FALSE);
                insert into t_17_01(f_17_01_00) values (FALSE);
                insert into t_17_01(f_17_01_00) values (FALSE);
                insert into t_17_01(f_17_01_00) values (FALSE);
                insert into t_17_01(f_17_01_00) values (FALSE);
                insert into t_17_01(f_17_01_00) values (FALSE);
            """
            ,
            """
                select v_17_00.f_17_01_00
                from v_17_00
                right join t_17_01 on
                    (
                        not -3298 <> coalesce(-934, 3710)
                    )
            """
            ,
            """
                select v_17_00.f_17_01_00
                from v_17_00
                right join t_17_01 on
                    (
                        not -3298 <> coalesce(-934, 3710)
                    )
                where (
                        (
                                0.80 = 0.73
                                and
                                (
                                        t_17_01.f_17_01_00
                                        and
                                        v_17_00.f_17_01_00
                                    )
                            ) = t_17_01.f_17_01_00
                      )
                UNION ALL
                select v_17_00.f_17_01_00
                from v_17_00
                right join t_17_01 on
                    (
                        not -3298 <> coalesce(-934, 3710)
                    )
                where (
                        not (
                                (
                                        0.80 = 0.73
                                        and
                                        (
                                                t_17_01.f_17_01_00
                                                and
                                                v_17_00.f_17_01_00
                                            )
                                    ) = t_17_01.f_17_01_00
                            )
                      )
                UNION ALL
                select v_17_00.f_17_01_00
                from v_17_00
                right join t_17_01 on
                    (
                        not -3298 <> coalesce(-934, 3710)
                    )
                where (
                        (
                                (
                                        0.80 = 0.73
                                        and
                                        (
                                                t_17_01.f_17_01_00
                                                and
                                                v_17_00.f_17_01_00
                                            )
                                    ) = t_17_01.f_17_01_00
                            ) is null
                      )
            """
        )
        ,
        # ==================== database18 ====================
        (
            """
                create table t_18_00(f_18_00_00 varchar(20) unique);
                create table t_18_01(f_18_01_00 smallint);
                create unique index i_18_00 on t_18_01(f_18_01_00);
                create view v_18_00 as select t_18_00.f_18_00_00 from t_18_00;
            """
            ,
            """
                insert into t_18_00(f_18_00_00) values ('fb');
                insert into t_18_01(f_18_01_00) values (143);
            """
            ,
            """
                select v_18_00.f_18_00_00
                from t_18_01
                left join t_18_00 on
                    false
                right join v_18_00 on
                    lower(t_18_00.f_18_00_00) >= t_18_00.f_18_00_00
            """
            ,
            """
                select v_18_00.f_18_00_00
                from t_18_01
                left join t_18_00 on
                    false
                right join v_18_00 on
                    lower(t_18_00.f_18_00_00) >= t_18_00.f_18_00_00
                where (
                        (
                                not true
                                and
                                v_18_00.f_18_00_00 in (t_18_00.f_18_00_00)
                            ) in (
                            (
                                    date '2020-02-29' between
                                        date '2000-01-01'
                                        and
                                        date '2000-01-01'
                            )
                        )
                      )
                UNION ALL
                select v_18_00.f_18_00_00
                from t_18_01
                left join t_18_00 on
                    false
                right join v_18_00 on
                    lower(t_18_00.f_18_00_00) >= t_18_00.f_18_00_00
                where (
                        not (
                                (
                                        not true
                                        and
                                        v_18_00.f_18_00_00 in (t_18_00.f_18_00_00)
                                    ) in (
                                    (
                                            date '2020-02-29' between
                                                date '2000-01-01'
                                                and
                                                date '2000-01-01'
                                    )
                                )
                            )
                      )
                UNION ALL
                select v_18_00.f_18_00_00
                from t_18_01
                left join t_18_00 on
                    false
                right join v_18_00 on
                    lower(t_18_00.f_18_00_00) >= t_18_00.f_18_00_00
                where (
                        (
                                (
                                        not true
                                        and
                                        v_18_00.f_18_00_00 in (t_18_00.f_18_00_00)
                                    ) in (
                                    (
                                            date '2020-02-29' between
                                                date '2000-01-01'
                                                and
                                                date '2000-01-01'
                                    )
                                )
                            ) is null
                      )
            """
        )
        ,
        # ==================== database19 ====================
        (
            """
                create table t_19_00(f_19_00_00 numeric(9, 2), f_19_00_01 varchar(20), f_19_00_02 boolean);
                create view v_19_00 as select t_19_00.f_19_00_00, t_19_00.f_19_00_02 from t_19_00;
                create index i_19_00 on t_19_00(f_19_00_00);
            """
            ,
            """
                insert into t_19_00(f_19_00_00, f_19_00_01, f_19_00_02) values (-3776.00, null, FALSE);
                insert into t_19_00(f_19_00_00, f_19_00_01, f_19_00_02) values (686.00, '', TRUE);
            """
            ,
            """
                select v_19_00.f_19_00_00
                from t_19_00
                right join v_19_00 on
                    v_19_00.f_19_00_02
            """
            ,
            """
                select v_19_00.f_19_00_00
                from t_19_00
                right join v_19_00 on
                    v_19_00.f_19_00_02
                where (
                        (
                                (t_19_00.f_19_00_00 is null) between
                                    v_19_00.f_19_00_02
                                    and
                                    (
                                            v_19_00.f_19_00_02
                                            and
                                            t_19_00.f_19_00_02
                                    )
                            ) in (
                            t_19_00.f_19_00_02,
                            t_19_00.f_19_00_02,
                            (cast(v_19_00.f_19_00_00 as bigint) is null)
                        )
                      )
                UNION ALL
                select v_19_00.f_19_00_00
                from t_19_00
                right join v_19_00 on
                    v_19_00.f_19_00_02
                where (
                        not (
                                (
                                        (t_19_00.f_19_00_00 is null) between
                                            v_19_00.f_19_00_02
                                            and
                                            (
                                                    v_19_00.f_19_00_02
                                                    and
                                                    t_19_00.f_19_00_02
                                            )
                                    ) in (
                                    t_19_00.f_19_00_02,
                                    t_19_00.f_19_00_02,
                                    (cast(v_19_00.f_19_00_00 as bigint) is null)
                                )
                            )
                      )
                UNION ALL
                select v_19_00.f_19_00_00
                from t_19_00
                right join v_19_00 on
                    v_19_00.f_19_00_02
                where (
                        (
                                (
                                        (t_19_00.f_19_00_00 is null) between
                                            v_19_00.f_19_00_02
                                            and
                                            (
                                                    v_19_00.f_19_00_02
                                                    and
                                                    t_19_00.f_19_00_02
                                            )
                                    ) in (
                                    t_19_00.f_19_00_02,
                                    t_19_00.f_19_00_02,
                                    (cast(v_19_00.f_19_00_00 as bigint) is null)
                                )
                            ) is null
                      )
            """
        )
        ,
        # ==================== database24 ====================
        (
            """
                create table t_24_00(f_24_00_00 char(8), f_24_00_01 timestamp unique, f_24_00_02 date);
                create index i_24_00 on t_24_00(f_24_00_00);
                create view v_24_00 as select t_24_00.f_24_00_00 from t_24_00;
            """
            ,
            """
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values ('', null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values (null, null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values (null, null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values (null, null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values (null, null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values ('', null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values ('bf', null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values (null, null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values ('ea', null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values (null, null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values ('', null, date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values (null, timestamp '2000-01-01 00:00:00.0000', date '2000-01-01');
                insert into t_24_00(f_24_00_00, f_24_00_01, f_24_00_02) values ('', timestamp '2020-02-29 12:00:00.0000', date '2000-01-01');
            """
            ,
            """
                select t_24_00.f_24_00_02
                from t_24_00
                right join v_24_00 on
                    false
            """
            ,
            """
                select t_24_00.f_24_00_02
                from t_24_00
                right join v_24_00 on
                    false
                where (
                        (
                                0.13 is null
                                and
                                t_24_00.f_24_00_02 >= t_24_00.f_24_00_02
                            ) > true
                      )
                UNION ALL
                select t_24_00.f_24_00_02
                from t_24_00
                right join v_24_00 on
                    false
                where (
                        not (
                                (
                                        0.13 is null
                                        and
                                        t_24_00.f_24_00_02 >= t_24_00.f_24_00_02
                                    ) > true
                            )
                      )
                UNION ALL
                select t_24_00.f_24_00_02
                from t_24_00
                right join v_24_00 on
                    false
                where (
                        (
                                (
                                        0.13 is null
                                        and
                                        t_24_00.f_24_00_02 >= t_24_00.f_24_00_02
                                    ) > true
                            ) is null
                      )
            """
        )
        ,
        # ==================== database26 ====================
        (
            """
                create table t_26_00(f_26_00_00 boolean);
                create view v_26_00 as select t_26_00.f_26_00_00 from t_26_00;
            """
            ,
            """
                insert into t_26_00(f_26_00_00) values (null);
                insert into t_26_00(f_26_00_00) values (null);
                insert into t_26_00(f_26_00_00) values (FALSE);
                insert into t_26_00(f_26_00_00) values (FALSE);
                insert into t_26_00(f_26_00_00) values (FALSE);
                insert into t_26_00(f_26_00_00) values (TRUE);
            """
            ,
            """
                select t_26_00.f_26_00_00
                from v_26_00
                right join t_26_00 on
                    (
                        (
                                cast(
                                        9580 + -4688
                                    as integer)
                            ) in (
                            427
                        )
                    )
            """
            ,
            """
                select t_26_00.f_26_00_00
                from v_26_00
                right join t_26_00 on
                    (
                        (
                                cast(
                                        9580 + -4688
                                    as integer)
                            ) in (
                            427
                        )
                    )
                where (
                        false > (
                                (
                                        t_26_00.f_26_00_00
                                        and
                                        v_26_00.f_26_00_00
                                    )
                                and
                                t_26_00.f_26_00_00
                            )
                      )
                UNION ALL
                select t_26_00.f_26_00_00
                from v_26_00
                right join t_26_00 on
                    (
                        (
                                cast(
                                        9580 + -4688
                                    as integer)
                            ) in (
                            427
                        )
                    )
                where (
                        not (
                                false > (
                                        (
                                                t_26_00.f_26_00_00
                                                and
                                                v_26_00.f_26_00_00
                                            )
                                        and
                                        t_26_00.f_26_00_00
                                    )
                            )
                      )
                UNION ALL
                select t_26_00.f_26_00_00
                from v_26_00
                right join t_26_00 on
                    (
                        (
                                cast(
                                        9580 + -4688
                                    as integer)
                            ) in (
                            427
                        )
                    )
                where (
                        (
                                false > (
                                        (
                                                t_26_00.f_26_00_00
                                                and
                                                v_26_00.f_26_00_00
                                            )
                                        and
                                        t_26_00.f_26_00_00
                                    )
                            ) is null
                      )
            """
        )
        ,
        # ==================== database29 ====================
        (
            """
                create table t_29_00(f_29_00_00 double precision);
                create table t_29_01(f_29_01_00 numeric(9, 2));
                create unique index i_29_00 on t_29_01(f_29_01_00);
                create unique index i_29_81 on t_29_01(f_29_01_00);
            """
            ,
            """
                insert into t_29_00(f_29_00_00) values (0.3600000000000000);
                insert into t_29_00(f_29_00_00) values (0.3600000000000000);
                insert into t_29_00(f_29_00_00) values (0.3600000000000000);
                insert into t_29_00(f_29_00_00) values (0.3600000000000000);
                insert into t_29_00(f_29_00_00) values (0.3600000000000000);
                insert into t_29_00(f_29_00_00) values (0.3600000000000000);
                insert into t_29_01(f_29_01_00) values (null);
                insert into t_29_01(f_29_01_00) values (null);
                insert into t_29_01(f_29_01_00) values (null);
                insert into t_29_01(f_29_01_00) values (null);
                insert into t_29_01(f_29_01_00) values (null);
                insert into t_29_01(f_29_01_00) values (null);
                insert into t_29_01(f_29_01_00) values (-7734.00);
            """
            ,
            """
                select t_29_00.f_29_00_00
                from t_29_01
                left join t_29_00 on
                    false
            """
            ,
            """
                select t_29_00.f_29_00_00
                from t_29_01
                left join t_29_00 on
                    false
                where (
                        (
                                t_29_00.f_29_00_00 <= t_29_00.f_29_00_00
                                and
                                false
                            ) in (
                            true
                        )
                      )
                UNION ALL
                select t_29_00.f_29_00_00
                from t_29_01
                left join t_29_00 on
                    false
                where (
                        not (
                                (
                                        t_29_00.f_29_00_00 <= t_29_00.f_29_00_00
                                        and
                                        false
                                    ) in (
                                    true
                                )
                            )
                      )
                UNION ALL
                select t_29_00.f_29_00_00
                from t_29_01
                left join t_29_00 on
                    false
                where (
                        (
                                (
                                        t_29_00.f_29_00_00 <= t_29_00.f_29_00_00
                                        and
                                        false
                                    ) in (
                                    true
                                )
                            ) is null
                      )
            """
        )
        ,
    ]
    # end of QRY_LIST definition 

    srv_cfg = driver_config.register_server(name = f'srv_cfg_9183', config = '')
    db_cfg_name = f'db_cfg_9183'
    db_cfg_object = driver_config.register_database(name = db_cfg_name)
    db_cfg_object.server.value = srv_cfg.name
    db_cfg_object.database.value = str(act.db.db_path)
    if act.is_version('>=5') and act.is_version('<6'):
        db_cfg_object.config.value = f"""
            OuterJoinConversion = true
        """

    mismatches_lst = []
    with connect(db_cfg_name, user = act.db.user, password = act.db.password) as con:
        cur = con.cursor()
        for ddl_lst, dml_lst, qry_ini, qry_tlp in QRY_LIST:
            try:
                for s in ddl_lst.split(';'):
                    if ( x := s.strip() ):
                        # run one of DDLs:
                        con.execute_immediate(x)
                con.commit()

                for s in dml_lst.split(';'):
                    if ( x := s.strip() ):
                        # run one of INSERTs:
                        con.execute_immediate(x)

                set_ini, set_tlp = [], []
                set_ini = Counter( cur.execute(qry_ini).fetchall() )
                set_tlp = Counter( cur.execute(qry_tlp).fetchall() )
                if set_ini == set_tlp:
                    pass
                else:
                    mismatches_lst.extend(
                        [ (ddl_lst, dml_lst, qry_ini, qry_tlp, set_ini, set_tlp) ]
                    )
            except DatabaseError as e:
                print(e.__str__())
                print(e.gds_codes)
            finally:
                con.commit()

    if mismatches_lst:
        print(f'{len(mismatches_lst)} mismatch(es) detected:')
        for i,x in enumerate(mismatches_lst):
            ddl_lst, dml_lst, qry_ini, qry_tlp, set_ini, set_tlp = x
            print(f'### MISMATCH N {i+1} ###')
            print('ddl_lst=', ddl_lst)
            print('-' * 40)
            print('dml_lst=', dml_lst)
            print('-' * 40)
            print('qry_ini=', qry_ini)
            print('-' * 40)
            print('qry_tlp=', qry_tlp)
            print('-' * 40)
            print(f'{set_ini=}')
            print(f'{set_tlp=}')

    else:
        print(EXPECTED_MSG)
    act.expected_stdout = EXPECTED_MSG
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
