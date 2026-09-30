#coding:utf-8
"""Shared helpers for the gbak FAST_PATH prototype tests.

Every backup/restore issued here goes through the Services Manager (`-se`) and
uses PARALLEL_WORKERS = 2, per the task requirement that worker count must stay
fixed so that normal vs fast comparisons are apples-to-apples.
"""
import subprocess
from pathlib import Path

import pytest

# The task fixes the number of parallel workers to 2 for all comparisons.
PARALLEL_WORKERS = 2

RICH_DDL = """
    -- one domain per checked datatype: ref_ columns of t_rich reference them,
    -- col_ columns declare the same type directly (both variants must survive
    -- the FAST_PATH transfer identically)
    create domain dm_sml smallint;
    create domain dm_int int;
    create domain dm_big bigint;
    create domain dm_i128 int128;
    create domain dm_flt float;
    create domain dm_real real;
    create domain dm_dbl double precision;
    create domain dm_lflt long float;
    create domain dm_num32 numeric(3,2);
    create domain dm_dec32 decimal(3,2);
    create domain dm_num92 numeric(9,2);
    create domain dm_dec92 decimal(9,2);
    create domain dm_num182 numeric(18,2);
    create domain dm_dec182 decimal(18,2);
    create domain dm_num3838 numeric(38,38);
    create domain dm_dec3838 decimal(38,38);
    create domain dm_df16 decfloat(16);
    create domain dm_df34 decfloat(34);
    create domain dm_date date;
    create domain dm_time time;
    create domain dm_ts timestamp;
    create domain dm_timetz time with time zone;
    create domain dm_tstz timestamp with time zone;
    create domain dm_bool boolean;
    create domain dm_ch1 char(1);
    create domain dm_ch200 char(200);
    create domain dm_nch1 nchar(1);
    create domain dm_nch200 nchar(200);
    create domain dm_vc1 varchar(1);
    create domain dm_vc200 varchar(200);
    create domain dm_blb_txt blob sub_type text;
    create domain dm_blb_bin blob sub_type 0;

    create table t_rich (
        id          integer not null primary key
       ,col_sml     smallint
       ,ref_sml     dm_sml
       ,col_int     int
       ,ref_int     dm_int
       ,col_big     bigint
       ,ref_big     dm_big
       ,col_i128    int128
       ,ref_i128    dm_i128
       ,col_flt     float
       ,ref_flt     dm_flt
       ,col_real    real
       ,ref_real    dm_real
       ,col_dbl     double precision
       ,ref_dbl     dm_dbl
       ,col_lflt    long float
       ,ref_lflt    dm_lflt
       ,col_num32   numeric(3,2)
       ,ref_num32   dm_num32
       ,col_dec32   decimal(3,2)
       ,ref_dec32   dm_dec32
       ,col_num92   numeric(9,2)
       ,ref_num92   dm_num92
       ,col_dec92   decimal(9,2)
       ,ref_dec92   dm_dec92
       ,col_num182  numeric(18,2)
       ,ref_num182  dm_num182
       ,col_dec182  decimal(18,2)
       ,ref_dec182  dm_dec182
       ,col_num3838 numeric(38,38)
       ,ref_num3838 dm_num3838
       ,col_dec3838 decimal(38,38)
       ,ref_dec3838 dm_dec3838
       ,col_df16    decfloat(16)
       ,ref_df16    dm_df16
       ,col_df34    decfloat(34)
       ,ref_df34    dm_df34
       ,col_date    date
       ,ref_date    dm_date
       ,col_time    time
       ,ref_time    dm_time
       ,col_ts      timestamp
       ,ref_ts      dm_ts
       ,col_timetz  time with time zone
       ,ref_timetz  dm_timetz
       ,col_tstz    timestamp with time zone
       ,ref_tstz    dm_tstz
       ,col_bool    boolean
       ,ref_bool    dm_bool
       ,col_ch1     char(1)
       ,ref_ch1     dm_ch1
       ,col_ch200   char(200)
       ,ref_ch200   dm_ch200
       ,col_nch1    nchar(1)
       ,ref_nch1    dm_nch1
       ,col_nch200  nchar(200)
       ,ref_nch200  dm_nch200
       ,col_vc1     varchar(1)
       ,ref_vc1     dm_vc1
       ,col_vc200   varchar(200)
       ,ref_vc200   dm_vc200
       ,col_blb_txt blob sub_type text
       ,ref_blb_txt dm_blb_txt
       ,col_blb_bin blob sub_type 0
       ,ref_blb_bin dm_blb_bin
    );
"""

RICH_ROWS = """
    -- row 1: extreme / boundary values for every datatype (int boundaries,
    -- float/double denormals and maxima, scaled numeric storage limits,
    -- decfloat exponent limits, max date/time, leap-day timestamp with tz)
    insert into t_rich (
        id, col_sml, ref_sml, col_int, ref_int, col_big, ref_big,
        col_i128, ref_i128, col_flt, ref_flt, col_real, ref_real,
        col_dbl, ref_dbl, col_lflt, ref_lflt,
        col_num32, ref_num32, col_dec32, ref_dec32,
        col_num92, ref_num92, col_dec92, ref_dec92,
        col_num182, ref_num182, col_dec182, ref_dec182,
        col_num3838, ref_num3838, col_dec3838, ref_dec3838,
        col_df16, ref_df16, col_df34, ref_df34,
        col_date, ref_date, col_time, ref_time, col_ts, ref_ts,
        col_timetz, ref_timetz, col_tstz, ref_tstz,
        col_bool, ref_bool,
        col_ch1, ref_ch1, col_ch200, ref_ch200,
        col_nch1, ref_nch1, col_nch200, ref_nch200,
        col_vc1, ref_vc1, col_vc200, ref_vc200,
        col_blb_txt, ref_blb_txt, col_blb_bin, ref_blb_bin
    )
    values (
        1, -32768, -32768, -2147483648, -2147483648,
        -9223372036854775808, -9223372036854775808,
        -170141183460469231731687303715884105728, -170141183460469231731687303715884105728,
        3.40282346638e38, 3.40282346638e38, 3.40282346638e38, 3.40282346638e38,
        1.7976931348623157e308, 1.7976931348623157e308, -9007199254740992, -9007199254740992,
        -327.68, -327.68, -327.68, -327.68,
        -21474836.48, -21474836.48, -21474836.48, -21474836.48,
        -92233720368547758.08, -92233720368547758.08, -92233720368547758.08, -92233720368547758.08,
        -0.99999999999999999999999999999999999999, -0.99999999999999999999999999999999999999,
        0.99999999999999999999999999999999999999, 0.99999999999999999999999999999999999999,
        -9.999999999999999E384, 9.999999999999999E384,
        -9.999999999999999999999999999999999E6144, 9.999999999999999999999999999999999E6144,
        '9999-12-31', '9999-12-31', '23:59:59.9999', '23:59:59.9999',
        '9999-12-31 23:59:59.9999', '9999-12-31 23:59:59.9999',
        '01:02:03.456 Indian/Cocos', '01:02:03.456 Indian/Cocos',
        '29.02.2004 01:02:03.456 Indian/Cocos', '29.02.2004 01:02:03.456 Indian/Cocos',
        true, true,
        'A', 'A', 'CHAR(200) ASCII LINE FOR FAST PATH RICH TYPE COVERAGE',
        'CHAR(200) ASCII LINE FOR FAST PATH RICH TYPE COVERAGE',
        'N', 'N', 'NCHAR(200) ASCII LINE FOR FAST PATH RICH TYPE COVERAGE',
        'NCHAR(200) ASCII LINE FOR FAST PATH RICH TYPE COVERAGE',
        'v', 'v', 'VARCHAR(200) ASCII LINE FOR FAST PATH RICH TYPE COVERAGE',
        'VARCHAR(200) ASCII LINE FOR FAST PATH RICH TYPE COVERAGE',
        'hello blob 0123456789012345678901234567890', 'hello blob 0123456789012345678901234567890',
        x'DEADBEEF0102030405', x'DEADBEEF0102030405'
    );

    -- row 2: all data columns are null (only the pk is set)
    insert into t_rich (id) values (2);

    -- row 3: opposite extremes and moderate values
    insert into t_rich (
        id, col_sml, ref_sml, col_int, ref_int, col_big, ref_big,
        col_i128, ref_i128, col_flt, ref_flt, col_real, ref_real,
        col_dbl, ref_dbl, col_lflt, ref_lflt,
        col_num32, ref_num32, col_dec32, ref_dec32,
        col_num92, ref_num92, col_dec92, ref_dec92,
        col_num182, ref_num182, col_dec182, ref_dec182,
        col_num3838, ref_num3838, col_dec3838, ref_dec3838,
        col_df16, ref_df16, col_df34, ref_df34,
        col_date, ref_date, col_time, ref_time, col_ts, ref_ts,
        col_timetz, ref_timetz, col_tstz, ref_tstz,
        col_bool, ref_bool,
        col_ch1, ref_ch1, col_ch200, ref_ch200,
        col_nch1, ref_nch1, col_nch200, ref_nch200,
        col_vc1, ref_vc1, col_vc200, ref_vc200,
        col_blb_txt, ref_blb_txt, col_blb_bin, ref_blb_bin
    )
    values (
        3, 32767, 32767, 2147483647, 2147483647,
        9223372036854775807, 9223372036854775807,
        170141183460469231731687303715884105727, 170141183460469231731687303715884105727,
        1.17549435082e-38, 1.17549435082e-38, 1.40129846432e-45, 1.40129846432e-45,
        -3e-308, -3e-308, 9007199254740992, 9007199254740992,
        327.67, 327.67, 327.67, 327.67,
        21474836.47, 21474836.47, 21474836.47, 21474836.47,
        92233720368547758.07, 92233720368547758.07, 92233720368547758.07, 92233720368547758.07,
        0.99999999999999999999999999999999999999, 0.99999999999999999999999999999999999999,
        -0.99999999999999999999999999999999999999, -0.99999999999999999999999999999999999999,
        1.0E-383, -1.0E-383,
        1.000000000000000000000000000000000E-6143, 0 /* plain zero: the literal 0E-6144 is rejected by the lexer ("overflow of the exponent") */,
        '0001-01-01', '0001-01-01', '00:00:00.0000', '00:00:00.0000',
        '0001-01-01 00:00:00.0000', '0001-01-01 00:00:00.0000',
        '00:00:00.0000 UTC', '00:00:00.0000 UTC',
        '2004-02-29 01:02:03.456 Indian/Cocos', '2004-02-29 01:02:03.456 Indian/Cocos',
        false, false,
        'z', 'z', 'char(200) lowercase ascii tail', 'char(200) lowercase ascii tail',
        'n', 'n', 'nchar(200) lowercase ascii tail', 'nchar(200) lowercase ascii tail',
        'w', 'w', 'varchar(200) lowercase ascii tail', 'varchar(200) lowercase ascii tail',
        '', '', x'', x''
    );
    commit;
"""

RICH_QUERY = """
    select
        id, col_sml, ref_sml, col_int, ref_int, col_big, ref_big,
        col_i128, ref_i128, col_flt, ref_flt, col_real, ref_real,
        col_dbl, ref_dbl, col_lflt, ref_lflt,
        col_num32, ref_num32, col_dec32, ref_dec32,
        col_num92, ref_num92, col_dec92, ref_dec92,
        col_num182, ref_num182, col_dec182, ref_dec182,
        col_num3838, ref_num3838, col_dec3838, ref_dec3838,
        col_df16, ref_df16, col_df34, ref_df34,
        col_date, ref_date, col_time, ref_time, col_ts, ref_ts,
        col_timetz, ref_timetz, col_tstz, ref_tstz,
        col_bool, ref_bool,
        col_ch1, ref_ch1, col_ch200, ref_ch200,
        col_nch1, ref_nch1, col_nch200, ref_nch200,
        col_vc1, ref_vc1, col_vc200, ref_vc200,
        col_blb_txt, ref_blb_txt, col_blb_bin, ref_blb_bin
    from t_rich
    order by id
"""


def svc_mngr(act) -> str:
    """Connection string of the tested server service manager, e.g. 'localhost/3600:service_mgr'."""
    host = act.host
    port = act.port
    return f"{host}/{port}:service_mgr" if port else f"{host}:service_mgr" if host else "service_mgr"


def gbak_backup(act, src: Path, fbk: Path, *, fast: bool, extra=None) -> None:
    sw = ["-se", svc_mngr(act), "-b", "-parallel", str(PARALLEL_WORKERS), "-v"]
    if fast:
        sw.append("-fast_path")
    sw += list(extra or [])
    sw += [str(src), str(fbk)]
    act.gbak(switches=sw)
    assert act.return_code == 0, f"backup failed (fast={fast}): {act.stderr}"
    assert act.stderr == "", f"unexpected gbak warnings on backup: {act.stderr}"
    act.reset()


def gbak_restore(act, fbk: Path, dst: Path, *, fast: bool, replace: bool = True,
                 extra=None, expect_fail: bool = False):
    sw = ["-se", svc_mngr(act)]
    sw.append("-rep" if replace else "-c")
    sw += ["-parallel", str(PARALLEL_WORKERS), "-v"]
    if fast:
        sw.append("-fast_path")
    sw += list(extra or [])
    sw += [str(fbk), str(dst)]
    if expect_fail:
        # a damaged stream makes gbak echo raw non-utf8 bytes (broken names,
        # lengths etc.); act.gbak decodes subprocess output strictly and would
        # die on UnicodeDecodeError, so run it with lenient decoding here.
        # This path does not store anything into act, so no reset is needed.
        params = [act.vars['gbak'], '-user', act.db.user, '-password', act.db.password] + sw
        p = subprocess.run(params, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        return p.returncode, p.stdout.decode('utf-8', errors='replace')
    act.gbak(switches=sw)
    assert act.return_code == 0, f"restore failed (fast={fast}): {act.stderr}"
    assert act.stderr == "", f"unexpected gbak warnings on restore: {act.stderr}"
    rc, out = act.return_code, act.stdout
    act.reset()
    return rc, out


def fetch_rows(act, sql: str):
    """Run a query on the primary test database and return all rows as a list."""
    with act.db.connect() as con:
        cur = con.cursor()
        cur.execute(sql)
        return cur.fetchall()


def fetch_rows_from(act_res, sql: str):
    """Same as fetch_rows() but for a secondary (restored) database fixture."""
    with act_res.db.connect() as con:
        cur = con.cursor()
        cur.execute(sql)
        return cur.fetchall()


def validated_clean(act, db_path: Path) -> None:
    """gfix -v -full must produce no output on a healthy database."""
    act.gfix(switches=["-v", "-full", str(db_path)], combine_output=True)
    assert act.stdout == "", f"validation found problems:\n{act.stdout}"
    act.reset()
