#coding:utf-8
#
# id:           bugs.core_4244
# title:        Problem with creation procedure which contain adding text in DOS864 charset
# decription:   
# tracker_id:   CORE-4244
# min_versions: ['2.5.2']
# versions:     2.5.2
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5.2
# resources: None

substitutions_1 = [('=.*', '')]

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create or alter procedure sp_test as
        declare char_one_byte char(1) character set dos864;
        declare str varchar(1000) character set dos864;
    begin
        char_one_byte='A';
        str='B';
        str=str||char_one_byte;
    end
    ^
    set term ;^
    commit;
    -- Confirmed for 2.1.7:
    -- Statement failed, SQLCODE = -802
    -- arithmetic exception, numeric overflow, or string truncation
    -- -Cannot transliterate character between character sets
    show proc sp_test;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Procedure text:
        declare char_one_byte char(1) character set dos864;
        declare str varchar(1000) character set dos864;
    begin
        char_one_byte='A';
        str='B';
        str=str||char_one_byte;
    end
  """

@pytest.mark.version('>=2.5.2')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

