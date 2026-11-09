#coding:utf-8

"""
ID:          issue-4723
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/4723
TITLE:       Optimize the record-level RLE algorithm for a denser compression of shorter-than-declared strings and sets of subsequent NULLs [CORE4401]
DESCRIPTION:
    Test creates table with nullable varchar column an adds lot of rows with incompressible data (GEN_UUID).
    Then we run gstat in order to parse statistics related to avg record length ('-r' switch).

    gstat reports for data pages and avg ratio following values:
    4.0.5.3099:
        Average record length: 33018.92, total records: 10000
        Average unpacked length: 32766.00, compression ratio: 0.99
        Pointer pages: 1, data page slots: 632
        Data pages: 632, average fill: 92%
    5.0.1.1399, 6.0.0.351:
        Average record length: 32757.00, total records: 10000
        Average unpacked length: 32766.00, compression ratio: 1.00
        Pointer pages: 1, data page slots: 304
        Data pages: 304, average fill: 87%.

    6.0.0.2446-0b6d977 (gstat fix 9bbc0e87, PR #9245):
        Average record length: 32766.00, total records: 10001
        Average unpacked length: 32766.00, compression ratio: 1.00
        Average fragment length: 8144.25, total fragments: 40004, max fragments: 4

    Since commit 9bbc0e87 ('fix(gstat): Use correct RHD, RHDE and RHDF based on header
    flags in gstat (#9245)') gstat subtracts fragment header size based on actual
    fragment flags: the last fragment of each record is stored with 13-byte RHD header
    rather than 22-byte RHDF, so 'average record length' no longer is understated by
    9 bytes per record (32766 = 2 bytes length prefix + 32760 data + ~4 bytes RLE
    service data). Therefore this value now MAY EXCEED declared column length;
    its upper bound = average unpacked length.

    Test assumes that values returned for 5.x will not be change in too wide range for several upcoming years
    in any order - see MIN_* and MAX_* thresholds.
NOTES:
    [20.05.2024] pzotov
        Improvement URL (27-sep-2022 15:16):
        https://github.com/FirebirdSQL/firebird/commit/54f1990b98d3e510a10d06fe9ceb76456804da52
        Improved record compression (denser encoding of repeating bytes and less blocks) (#7302)
        Charset must be specified in db_factory, otherwise 'malformed string' will raise.
        Checked on 5.0.1.1399, 6.0.0.351 for DB with page_size = 8192.
    [09.11.2026] pzotov
        DISABLED because test 'gh_9245_test.py' (AI-generated) does the same but with more careful checks.
"""
import re

import pytest
import platform
from firebird.qa import *

N_ROWS = 10000
N_WIDT = 32760

MIN_DP_COUNT_THRESHOLD = 280
MAX_DP_COUNT_THRESHOLD = 330

COMPRESSION_THRESHOLD = 1.00

init_ddl = f"""
    recreate table test (f01 varchar({N_WIDT}) character set octets not null);
    commit;

    set term ^;
    execute block as
        declare n int = {N_ROWS};
    begin
        while (n > 0) do
        begin
            insert into test(f01) values( lpad('', 32760, gen_uuid()) );
            n = n - 1;
        end
    end
    ^
    set term ;^
    commit;
"""

db = db_factory(page_size = 8192, init = init_ddl, charset = 'win1251')
act = python_act('db')

@pytest.mark.skip("DISABLED: see gh_9245_test.py")
@pytest.mark.version('>=5.0')
def test_1(act: Action, capsys):

    act.gstat(switches=['-r', '-t', 'TEST', '-user', act.db.user, '-pass', act.db.password])
    gstat_lines = act.stdout.splitlines()

    #for p in gstat_lines:
    #    print(p)
    #
    #act.expected_stdout = f"""
    #"""
    #act.stdout = capsys.readouterr().out
    #assert act.clean_stdout == act.clean_expected_stdout

    
    # Average record length: N.FF, total records: M
    # NB: value <N.FF> is length of the PACKED record data (2 bytes length prefix + column data
    # + RLE service bytes), so it MAY exceed declared column length. Its upper bound is
    # average unpacked length, i.e. record format size.
    p_average_record_length = re.compile( r'Average\s+record\s+length(:)?\s+\d+(.\d+)?' )

    # Average unpacked length: N.FF, compression ratio: R.PP
    # NB: for improved RLE value <R.PP> must be 1.00 because column contrains incompressible data
    p_compression_ratio = re.compile( r'Average\s+unpacked\s+length(:)?\s+\d+(.\d+)?(,)?\s+compression\s+ratio:\s+\d+(.\d+)?' )

    # the same line as above, but we need value <N.FF> separately: it serves as the upper bound
    # for average record length
    p_average_unpacked_length = re.compile( r'Average\s+unpacked\s+length(:)?\s+\d+(.\d+)?' )

    # Pointer pages: N, data page slots: M
    p_pointer_pages_data_pages_slots = re.compile( r'Pointer\s+pages(:)?\s+\d+(,)?\s+data\s+page\s+slots(:)?\s+\d+' )

    average_record_length = average_unpacked_length = compression_ratio = data_pages_cnt = -1
    gstat_lines = act.stdout.splitlines()
    for line in gstat_lines:
        if p_average_record_length.search(line):
            # 'Average record length: 32757.00, total records: 10000' --> 32757
            average_record_length = int(float(line.replace(',','').split()[3]))
        if p_average_unpacked_length.search(line):
            # 'Average unpacked length: 32766.00, compression ratio: 1.00' --> 32766
            average_unpacked_length = int(float(line.replace(',','').split()[3]))
        if p_compression_ratio.search(line):
            # 'Average unpacked length: 32766.00, compression ratio: 1.00'
            compression_ratio = float(line.split()[-1])
        if p_pointer_pages_data_pages_slots.search(line):
            data_pages_cnt = int(line.split()[-1])

    
    assert average_record_length > 0 and average_unpacked_length > 0 and compression_ratio > 0 and data_pages_cnt > 0

    avg_rec_len_expected_msg = f'average_record_length -- expected: LESS OR EQUALS to average unpacked length = {average_unpacked_length}'
    if average_record_length <= average_unpacked_length:
        print(avg_rec_len_expected_msg)
    else:
        print(f'average_record_length -- UNEXPECTED: {average_record_length} - more than average unpacked length = {average_unpacked_length}')

    #-------------------------------------------------------------------------------------------
    compression_ratio_expected_msg = f'compression_ratio_expected_msg -- expected: >= {COMPRESSION_THRESHOLD}'
    if compression_ratio >= COMPRESSION_THRESHOLD:
        print(compression_ratio_expected_msg)
    else:
        print(f'compression_ratio -- UNEXPECTED: {compression_ratio} - less than {COMPRESSION_THRESHOLD} (wasted compression occurred)')
    
    #-------------------------------------------------------------------------------------------
    data_pages_cnt_expected_msg = f'data_pages_cnt: expected, within {MIN_DP_COUNT_THRESHOLD=} ... {MAX_DP_COUNT_THRESHOLD=}'
    if data_pages_cnt >= MIN_DP_COUNT_THRESHOLD and data_pages_cnt <= MAX_DP_COUNT_THRESHOLD:
        print(data_pages_cnt_expected_msg)
    else:
        print(f'data_pages_cnt UNEXPECTED: {data_pages_cnt=} -- out of scope: {MIN_DP_COUNT_THRESHOLD=} ... {MAX_DP_COUNT_THRESHOLD=}')

    act.expected_stdout = f"""
        {avg_rec_len_expected_msg}
        {compression_ratio_expected_msg}
        {data_pages_cnt_expected_msg}
    """
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
