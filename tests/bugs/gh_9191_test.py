#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9191
TITLE:       Converting TIME WITH TIME ZONE to TIME costs about 4 times more than the equivalent TIMESTAMP conversion with a region session time zone
DESCRIPTION:
    Test measures CPU time that is spent for loop of <N_CUT_OFF_COUNT> iterations, in each of which TIME ZONE part is cuted-off from
    from CURRENT_TIME[STAMP] value (by assigning this value to variable declared as `time` or `timestamp`, i.e. without time zone).
    Before loop, we set time zone by specifying TWO OPPOSITE cases (for which valuable difference did exist prior fix):
        1) using UTC offset, e.g.: SET TIME ZONE '+06:30';
        2) using IANA time zone name, e.g. SET TIME ZONE 'Indian/Cocos';
    These cases are processed in `for tz_format in ('UTC_offset', 'IANA_tz_nm')`.

    Each measurement is performed twise (results are compared independently): for `TIME WITH TIME ZONE` and `TIMESTAMP WITH TIME ZONE`.
    These types of conversion are processed in `for t_type in ('time_with_tz', 'timestamp_with_tz')`

    Total number of measurements for each combination of (tz_format, t_type) is determined by setting `N_MEASURES`.
    Finally, we get ratio between medians of these measures (see `tm_cut_off_median` and `ts_cut_off_median`).
    Test is considered as passed if these median ratios less than appropriate thresholds (MAX_TM_RATIO and MAX_TS_RATIO).
NOTES:
    [10.10.2026] pzotov.
    Before fix ratio `tm_cut_off_median` was ~2.62 (i.e. performance was poor for converting from `time with time zone` to `time`
    if data was specified in `IANA timezone ID` format). After fix this ratio became ~1.30.
    No valuable difference was found for `TIMESTAMP WITH TIME ZONE` -> `TIMESTAMP`.

    Confirmed problem on 6.0.0.2199-bf94598.
    Checked on 6.0.0.2204-2d20c77.
"""
import psutil
import pytest
from firebird.qa import *

###########################
###   S E T T I N G S   ###
###########################

# How many times we do measure:
N_MEASURES = 7

# How many iterations must be done within loop:
N_CUT_OFF_COUNT = 500000

# Maximal value for ratio between maximal and minimal medians
#
##################
MAX_TM_RATIO = 1.8
MAX_TS_RATIO = 1.6
##################

init_script = """
    create domain dm_what varchar(20) check (value in ('time_with_tz', 'timestamp_with_tz'));
    set term ^;
    create procedure sp_cut_off_timezone (
        a_iter_cnt int
        ,a_tz varchar(50)
        ,a_from_what dm_what
    ) as
        declare i int;
        declare tm time;
        declare ts timestamp;
    begin
        execute statement 'set time zone ''' || a_tz || '''';
        i = 0;
        if ( a_from_what = 'time_with_tz' ) then
            while (i < a_iter_cnt) do
            begin
                tm = current_time;
                i = i + 1;
            end
        else
            while (i < a_iter_cnt) do
            begin
                ts = current_timestamp;
                i = i + 1;
            end
    end
    ^
    set term ;^
    commit;
"""

db = db_factory(init = init_script)
act = python_act('db')

@pytest.mark.perf_measure
@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    with act.db.connect() as con:
        cur=con.cursor()
        cur.execute('select mon$server_pid as p from mon$attachments where mon$attachment_id = current_connection')
        fb_pid = int(cur.fetchone()[0])

        times_map = {}
        t_map = {}
        # UTC_offset
        # IANA_tz_nm

        for tz_format in ('UTC_offset', 'IANA_tz_nm'):
            tz_value = '+06:30' if tz_format == 'UTC_offset' else 'indian/Cocos'
            for t_type in ('time_with_tz', 'timestamp_with_tz'):
                for i in range(N_MEASURES):
                    fb_cpu_0 = psutil.Process(fb_pid).cpu_times()
                    
                    cur.callproc( 'sp_cut_off_timezone', (N_CUT_OFF_COUNT, tz_value, t_type) )
                    fb_cpu_1 = psutil.Process(fb_pid).cpu_times()

                    times_map[ tz_format, t_type, i ]  = max(fb_cpu_1.user - fb_cpu_0.user, 0.000001)

    utc_offset_tm_cut_off_median = median( [v for k,v in times_map.items() if k[0] == 'UTC_offset' and k[1] == 'time_with_tz'] )
    utc_offset_ts_cut_off_median = median( [v for k,v in times_map.items() if k[0] == 'UTC_offset' and k[1] == 'timestamp_with_tz'] )

    iana_tz_nm_tm_cut_off_median = median( [v for k,v in times_map.items() if k[0] == 'IANA_tz_nm' and k[1] == 'time_with_tz'] )
    iana_tz_nm_ts_cut_off_median = median( [v for k,v in times_map.items() if k[0] == 'IANA_tz_nm' and k[1] == 'timestamp_with_tz'] )

    expected_lst = []
    MSG_COMMON_STR = 'Ratio between medians of CPU times when TZ-part is removed from IANA_TZ_NAME *vs* UTC_OFFSET values'
    TM_MSG_PREFIX = f'Datatype: `TIME`. {MSG_COMMON_STR}: '
    TS_MSG_PREFIX = f'Datatype: `TIMESTAMP`. {MSG_COMMON_STR}: '

    all_fine = 1
    tm_cut_off_median = iana_tz_nm_tm_cut_off_median / utc_offset_tm_cut_off_median
    ts_cut_off_median = iana_tz_nm_ts_cut_off_median / utc_offset_ts_cut_off_median

    if tm_cut_off_median <= MAX_TM_RATIO:
        s = TM_MSG_PREFIX + 'acceptable.'
        expected_lst.append(s)
        print(s)
    else:
        print(TM_MSG_PREFIX + f'too big: {tm_cut_off_median} -- greater than {MAX_TM_RATIO}')
        all_fine = 0

    if ts_cut_off_median <= MAX_TS_RATIO:
        s = TS_MSG_PREFIX + 'acceptable.'
        expected_lst.append(s)
        print(s)
    else:
        print(TS_MSG_PREFIX + f'too big: {ts_cut_off_median} -- greater than {MAX_TS_RATIO}')
        all_fine = 0

    if all_fine:
        pass
    else:
        print('times_map:')
        for k,v in times_map.items():
            print(k,':::',v)

        print(f'{utc_offset_tm_cut_off_median=}')
        print(f'{utc_offset_ts_cut_off_median=}')
        print(f'{iana_tz_nm_tm_cut_off_median=}')
        print(f'{iana_tz_nm_ts_cut_off_median=}')

        print(f'{iana_tz_nm_tm_cut_off_median/utc_offset_tm_cut_off_median=}')
        print(f'{iana_tz_nm_ts_cut_off_median/utc_offset_ts_cut_off_median=}')

    # Expected output must be like this:
    # Datatype: `TIME`. Ratio between medians of CPU times when TZ-part is removed from IANA_TZ_NAME *vs* UTC_OFFSET values: acceptable.
    # Datatype: `TIMESTAMP`. Ratio between medians of CPU times when TZ-part is removed from IANA_TZ_NAME *vs* UTC_OFFSET values: acceptable.

    act.expected_stdout = '\n'.join( expected_lst )
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
