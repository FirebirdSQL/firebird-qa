#coding:utf-8
#
# id:           bugs.core_4739
# title:        Accent insensitive comparison: diacritical letters with DIAGONAL crossing stroke pass only test on EQUALITY to their non-accented forms
# decription:   
#                   Confirmed successful result on 4.0.0.1627
#               	All builds before that failed on four characters: 'Ø' 'Ð' 'Ł' and 'Ŀ'.
#                
# tracker_id:   CORE-4739
# min_versions: ['4.0']
# versions:     4.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 4.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    create collation co_utf8_ci_ai for utf8 from unicode case insensitive accent insensitive; 
    commit;

    set list on;
    set count on;

    with recursive 
    d as ( 
        select 
         cast( 'ḂĊḊḞĠṀṖṠṪ' || 'ẀẂŴŶ' || 'ŠŽ' || 'Ø' || 'Ð' || 'Ł' || 'Ŀ' || 'ĘĄĂÂÎŢŐŰĖÅĽĢÁÉÍÓÚÝÀÈÌÒÙÂÊÎÔÛÃÑÕÄËÏÖÜŸÇŠĄĘŹŻĂŞŢ' as varchar(80) character set utf8) s
        ,cast( 'BCDFGMPST' || 'WWWY' || 'SZ' || 'O' || 'D' || 'L' || 'L' || 'EAAAITOUEALGAEIOUYAEIOUAEIOUANOAEIOUYCSAEZZAST' as varchar(80) character set utf8) ascii_only_char
        from rdb$database 
    ) 
    ,r as(select 1 i from rdb$database union all select r.i+1 from r where r.i < 100) 
    ,e as( 
        select 
             substring(d.s from r.i for 1) non_ascii_char 
            ,substring(d.ascii_only_char from r.i for 1) ascii_only_char 
        from d join r on r.i <= char_length(d.s) 
    ) 
    ,f as ( 
        select 
             e.non_ascii_char --as utf_char
            ,e.ascii_only_char
            ,iif( e.non_ascii_char collate co_utf8_ci_ai = e.ascii_only_char, 1, 0 ) equal_test 
            ,iif( e.non_ascii_char collate co_utf8_ci_ai between e.ascii_only_char and e.ascii_only_char, 1, 0 ) between_test
            ,iif( position(e.ascii_only_char, e.non_ascii_char collate co_utf8_ci_ai) >0 , 1, 0 ) pos_test 
            ,iif( e.non_ascii_char collate co_utf8_ci_ai starting with e.ascii_only_char, 1, 0 ) start_with_test 
            ,iif( e.non_ascii_char collate co_utf8_ci_ai like e.ascii_only_char, 1, 0 ) like_test 
            ,iif( e.non_ascii_char collate co_utf8_ci_ai containing e.ascii_only_char, 1, 0 ) containing_test
            ,iif( e.non_ascii_char collate co_utf8_ci_ai similar to e.ascii_only_char, 1, 0 ) similar_to_letter_test 
            ,iif( e.non_ascii_char collate co_utf8_ci_ai similar to '[[:ALPHA:]]', 1, 0 ) similar_to_alpha_test 
        from e 
    ) 
    select * 
    from f 
    where minvalue( equal_test, between_test, pos_test, start_with_test, like_test, containing_test, similar_to_letter_test, similar_to_alpha_test  ) = 0
    order by non_ascii_char
    ; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    Records affected: 0
  """

@pytest.mark.version('>=4.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

