#coding:utf-8

"""
ID:          issue-1957
ISSUE:       1957
TITLE:       select * from rdb$triggers where rdb$trigger_source like 'CHECK%'
DESCRIPTION:
JIRA:        CORE-1539
"""

import pytest
from firebird.qa import *

init_script = """
	-- ### ONCE AGAIN ###
	-- 1) for checking this under ISQL following must be encoded in WIN1251
	-- 2) for running under fbt_run utility following must be encoded in UTF8.
    recreate table test (
        bugtype         varchar(20),
        bugfrequency    varchar(20),
        decision        varchar(20),
        fixerkey        int,
        decisiondate date
    );

    alter table test
        add constraint test_bugtype check (bugtype in ('зрабіць', 'трэба зрабіць', 'недахоп', 'памылка', 'катастрофа'))
        ,add constraint test_bugfrequency check (bugfrequency in ('ніколі', 'зрэдку', 'часам', 'часта', 'заўсёды', 'не прыкладаецца'))
        ,add constraint test_decision check (decision in ('адкрыта', 'зроблена', 'састарэла', 'адхілена', 'часткова', 'выдалена'))
        ,add constraint test_fixerkey check ((decision = 'адкрыта' and fixerkey is null and decisiondate is null) or (decision <> 'адкрыта' and not fixerkey is null and not decisiondate is null))
    ;
    commit;
"""

db = db_factory(charset='UTF8', init=init_script)

test_script = """
set blob all;
set list on;
-- Ticket:
-- select * from rdb$triggers where rdb$trigger_source like 'CHECK%%' ==> "Cannot transliterate character between character sets."
-- select * from rdb$triggers where rdb$trigger_source starting 'CHECK' ==> works fine.
select rdb$trigger_name, rdb$trigger_source
from rdb$triggers
where rdb$trigger_source like 'check%%'
order by cast(replace(rdb$trigger_name, 'CHECK_', '') as int);
"""

act = isql_act('db', test_script,
                 substitutions=[('RDB$TRIGGER_SOURCE.*', 'RDB$TRIGGER_SOURCE              <VALUE>')])

expected_stdout = """

RDB$TRIGGER_NAME                CHECK_1
RDB$TRIGGER_SOURCE              0:b
check (bugtype in ('зрабіць', 'трэба зрабіць', 'недахоп', 'памылка', 'катастрофа'))

RDB$TRIGGER_NAME                CHECK_2
RDB$TRIGGER_SOURCE              0:e
check (bugtype in ('зрабіць', 'трэба зрабіць', 'недахоп', 'памылка', 'катастрофа'))

RDB$TRIGGER_NAME                CHECK_3
RDB$TRIGGER_SOURCE              0:11
check (bugfrequency in ('ніколі', 'зрэдку', 'часам', 'часта', 'заўсёды', 'не прыкладаецца'))

RDB$TRIGGER_NAME                CHECK_4
RDB$TRIGGER_SOURCE              0:14
check (bugfrequency in ('ніколі', 'зрэдку', 'часам', 'часта', 'заўсёды', 'не прыкладаецца'))

RDB$TRIGGER_NAME                CHECK_5
RDB$TRIGGER_SOURCE              0:17
check (decision in ('адкрыта', 'зроблена', 'састарэла', 'адхілена', 'часткова', 'выдалена'))

RDB$TRIGGER_NAME                CHECK_6
RDB$TRIGGER_SOURCE              0:1a
check (decision in ('адкрыта', 'зроблена', 'састарэла', 'адхілена', 'часткова', 'выдалена'))

RDB$TRIGGER_NAME                CHECK_7
RDB$TRIGGER_SOURCE              0:1d
check ((decision = 'адкрыта' and fixerkey is null and decisiondate is null) or (decision <> 'адкрыта' and not fixerkey is null and not decisiondate is null))

RDB$TRIGGER_NAME                CHECK_8
RDB$TRIGGER_SOURCE              0:20
check ((decision = 'адкрыта' and fixerkey is null and decisiondate is null) or (decision <> 'адкрыта' and not fixerkey is null and not decisiondate is null))
"""

@pytest.mark.version('>=3')
def test_1(act: Action):
    act.expected_stdout = expected_stdout
    act.execute(charset='WIN1251')
    assert act.clean_stdout == act.clean_expected_stdout


