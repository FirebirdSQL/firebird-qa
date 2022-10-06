#coding:utf-8

"""
ID:          issue-3848
ISSUE:       3848
TITLE:       Blob transliteration may not happen inside the union
DESCRIPTION:
JIRA:        CORE-3489
FBTEST:      bugs.core_3489
NOTES:
    [06.10.2022] pzotov
        Could not complete adjusting for LINUX in new-qa.
        DEFERRED.
"""
import platform
import pytest
from pathlib import Path
from firebird.qa import *

init_script = """
	set term ^;
	create or alter procedure sp_test
	returns (
		msg_blob_id blob sub_type 1 segment size 80 character set unicode_fss)
	AS
	begin
		msg_blob_id= 'Это проверка на вывод строки "Йцукёнг"'; -- text in cyrillic
		suspend;
	end
	^
	set term ;^
	commit;
"""

db = db_factory(charset='WIN1251', init=init_script)

act = python_act('db', substitutions=[('MSG_BLOB_ID.*', '')])

expected_stdout = """
    Это проверка на вывод строки "Йцукёнг"
    Это проверка на вывод строки "Йцукёнг"
    Records affected: 2
"""

script_file = temp_file('test_script.sql')

@pytest.mark.skipif(platform.system() != 'Windows', reason='FIXME: see notes')
@pytest.mark.version('>=3')
def test_1(act: Action, script_file: Path):
    script_file.write_text("""
    set list on;
    set blob all;
    set count on;
    set list on;

    select msg_blob_id
    from sp_test
    union
    select msg_blob_id
    from sp_test;
    """, encoding='cp1251')
    act.expected_stdout = expected_stdout
    act.isql(switches=[], input_file=script_file, charset='WIN1251')
    assert act.clean_stdout == act.clean_expected_stdout


