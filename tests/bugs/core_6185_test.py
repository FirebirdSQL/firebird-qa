#coding:utf-8
#
# id:           bugs.core_6185
# title:        Some (wrong ?) parameters of ENCRYPT() leads FB to crash
# decription:
#                   Confirmed crash on 4.0.0.1637.
#                   Checked on 4.0.0.1691 SS: OK, 1.658s.
#
# tracker_id:   CORE-6185
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    set blob all;

    create or alter procedure sp_block_test(a_alg varchar(30)) as begin end;
    commit;

    recreate table test( crypto_alg varchar(30), source_text blob, crypto_key varchar(128), crypto_iv varchar(16) );
    commit;

    insert into test( crypto_alg, source_text,                 crypto_key,         crypto_iv )
              values( 'AES',      lpad('', 65533, gen_uuid()), '0101010101010101', lpad('',16, uuid_to_char( gen_uuid() )) );
    commit;

    set term ^;
    create or alter procedure sp_block_test( a_alg varchar(30) ) returns( result_msg varchar(80) )
    as
        declare v_encrypted blob;
        declare v_encrypt_sttm blob;
    begin
        for
            select
                 t.source_text
                ,t.crypto_alg
                ,t.crypto_key
                ,t.crypto_iv
            from test t
            where upper( t.crypto_alg ) = upper( :a_alg )
            as cursor c
        do begin
            v_encrypt_sttm = 'select encrypt( q''{' || c.source_text || '}'' using ' || c.crypto_alg || ' mode ofb key q''{' || c.crypto_key || '}'' iv q''{' || c.crypto_iv || '}'' ) from rdb$database';
            execute statement v_encrypt_sttm into v_encrypted;
        end
        result_msg = 'String has been encrypted.';
        suspend;
    end
    ^
    set term ;^
    commit;

    select result_msg from sp_block_test('aes');
    select encrypt( 'fooriobar' using CHACHA20 key q'{1110FB89-AD32-4E}' iv q'{114E811E}' counter cast(null as bigint) ) as encrypt_str from rdb$database;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    RESULT_MSG                      String has been encrypted.
    ENCRYPT_STR                     8E709DDA89912F172C
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.charset = 'NONE'
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

