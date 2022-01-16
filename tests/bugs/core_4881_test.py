#coding:utf-8
#
# id:           bugs.core_4881
# title:        Increase maximum string literal length to 64K (bytes) while setting a lower limit (of characters) for multibyte charsets based on their max char. length (UTF-8 literals will be limited to 16383 characters)
# decription:
#               Test verifies that one may to operate with string literals:
#               1) containing only ascii characters (and limit for this case should be 65535 bytes (=chars))
#               2) containing unicode characters but all of them requires 3 bytes for encoding (and limit for this should be 16383 character)
#               3) containing literals with mixed byte-per-character encoding requirement (limit should be also 16383 character).
#               Before 3.0.0.31981 following statement raises:
#               String literal with 65536 bytes exceeds the maximum length of 32767 bytes
# tracker_id:   CORE-4881
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from zipfile import Path
#from pathlib import Path
#from zipfile import ZipFile, ZIP_DEFLATED
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
	O_LEN_ASCII_ONLY                65535
	C_LEN_ASCII_ONLY                65535
	O_LEN_UTF8_3BPC                 49149
	C_LEN_UTF8_3BPC                 16383
	O_LEN_UTF8_MIXED                19889
	C_LEN_UTF8_MIXED                16383
"""

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    script_file = Path(act_1.files_dir / 'core_4881.zip',
                       at='core_4881_script.sql')
    act_1.script = script_file.read_text(encoding='utf-8')
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

