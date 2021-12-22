#coding:utf-8
#
# id:           bugs.core_4436
# title:        Support for different hash algorithms in HASH system function
# decription:   
#                  Test verifies only:
#                  1) ability to use syntax: hash(<string> using <algo>)
#                  2) non-equality of hash results for sha1, sha256 and sha512 using _TRIVIAL_ sample from ticket.
#                  build 4.0.0.713: OK, 1.094s.
#               
#                  Note that for strings:
#                  '20177527e04e05d5e7b448c1ab2b872f86831d0b' and '20177527e04e05d5e7b448c1ab2b872f86831d0b'
#                  - current imlpementation of SHA1, SHA256 and SHA512 gives the same hash value.
#                  (See: https://stackoverflow.com/questions/3475648/sha1-collision-demo-example )
#               
#                  NOTE. Since build 4.0.0.2180 (27.08.2020) we have to use *new* function for cryptograpic hashes
#                  when addition argument for algorithm is used: crypt_hash().
#                
# tracker_id:   CORE-4436
# min_versions: ['4.0.0']
# versions:     4.0
# qmid:         

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;

    recreate table test(s varchar(32765));
    commit;
    insert into test(s) values('4-20100433-01775-LOTES');
    insert into test(s) values('1-20100433-01765-LOTES');
    commit;

    select -(count(s) - count(distinct hash(s))) as hash_default_result from test;

    select -(count(s) - count(distinct crypt_hash(s using sha1))) as hash_sha1_result from test;
    select -(count(s) - count(distinct crypt_hash(s using sha256))) as hash_sha256_result from test;
    select -(count(s) - count(distinct crypt_hash(s using sha512))) as hash_sha512_result from test;

    /*
    Used before 27.08.2020:
    select -(count(s) - count(distinct hash(s using sha1))) as hash_sha1_result from test;
    select -(count(s) - count(distinct hash(s using sha256))) as hash_sha256_result from test;
    select -(count(s) - count(distinct hash(s using sha512))) as hash_sha512_result from test;
    */
"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    HASH_DEFAULT_RESULT             -1
    HASH_SHA1_RESULT                0
    HASH_SHA256_RESULT              0
    HASH_SHA512_RESULT              0
"""

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

