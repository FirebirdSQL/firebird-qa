#coding:utf-8
#
# id:           bugs.core_6542
# title:        Implementation of SUBSTRING for UTF8 character set is inefficient
# decription:   
#                   Confirmed issues on 4.0.0.2422 and 3.0.8.33345: ratio is about 16x ... 17x.
#                   Checked on 4.0.0.2425 and 3.0.8.33349: ratio is about 1.05 ... 1.07.
#                   Decided to use threshold = 1.15 for check performance ratio.
#                 
# tracker_id:   CORE-6542
# min_versions: ['3.0.8']
# versions:     3.0.8
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0.8
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    execute block as
        declare str1 varchar(8000) character set unicode_fss;
        declare str2 varchar(10) character set unicode_fss;
        declare n int = 100000;
        declare t0 timestamp;
        declare t1 timestamp;
    begin
        str1 = LPAD('abcd', 8000, '--');
        t0 = 'now';
        while (n > 0) do
        begin
            str2 = SUBSTRING(str1 from 1 FOR 10);
            n = n - 1;
        end
        t1 = 'now';
        rdb$set_context('USER_SESSION', 'TIME_UFSS', datediff(millisecond from t0 to t1) );
    end
    ^
    execute block as
        declare str1 varchar(8000) character set utf8;
        declare str2 varchar(10) character set utf8;
        declare n int = 100000;
        declare t0 timestamp;
        declare t1 timestamp;
    begin
        str1 = LPAD('abcd', 8000, '--');
        t0 = 'now';
        while (n > 0) do
        begin
            str2 = SUBSTRING(str1 from 1 FOR 10);
            n = n - 1;
        end
        t1 = 'now';
        rdb$set_context('USER_SESSION', 'TIME_UTF8', datediff(millisecond from t0 to t1) );
    end
    ^
    set term ;^

    set list on;
    select iif( r < threshold, 'acceptable.', 'POOR: ' || r || ' - exceeds threshold = ' || threshold) as "UTF8_substring_performance:"
    from (
        select
            1.000 * cast( rdb$get_context('USER_SESSION', 'TIME_UTF8') as int) / cast( rdb$get_context('USER_SESSION', 'TIME_UFSS') as int) as r
           ,1.15 as threshold
        from rdb$database
    );

"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    UTF8_substring_performance:     acceptable.
"""

@pytest.mark.version('>=3.0.8')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

