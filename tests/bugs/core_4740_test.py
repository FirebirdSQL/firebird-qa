#coding:utf-8
#
# id:           bugs.core_4740
# title:        SIMILAR TO with quantifier {n,} in the pattern: 1) fails on 2.5 ("Invalid pattern"), 2) strange result in 3.0
# decription:   
# tracker_id:   CORE-4740
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(page_size=4096, sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    with
    d(txt,ptn) as(
      select
        'abcZ', '[[:lower:]]{1,}Z' from rdb$database union all select
        'abcz', '[[:lower:]]{1,}z' from rdb$database union all select
        'abcz', '[[:lower:]]*z' from rdb$database union all select
        'abcz', '[[:lower:]]+z' from rdb$database union all select
        'aggagg', '([[:lOwEr:]]{1}gg){2,}' from rdb$database union all select
        'aggagg', '([[:lOWeR:]]{1,}gg){2,}' from rdb$database union all select
        'aggagg', '(a{1}gg){2}' from rdb$database union all select
        'aggagg', '(a{0,}gg){2}' from rdb$database union all select
        'aggagg', '(a{1}__){2}' from rdb$database union all select
        'aggagg', '(a{1}__){1,}' from rdb$database union all select
        'aggagg', '(a{1}[b-z]{2}){2}' from rdb$database union all select
        'XabaXa', '([X](a|b){1,3}){2}' from rdb$database union all select
        'XabaXaba', '([X](a|b){3}){2}' from rdb$database union all select
        'XabaX', '([X](a|b){0,3}){1,}' from rdb$database union all select
        'XabaX', '([X](a|b){0,3}){2}' from rdb$database union all select
        'XaX', '([X](a){0,1}){2}' from rdb$database union all select
        'XaXa', '([X](a){1}){2}' from rdb$database union all select
        'XaXa', '([X]a{1}){2}' from rdb$database
    )
    select txt, ptn, case when trim(txt) similar to trim(ptn) then 1 else 0 end is_match
    from d; 
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    TXT                             abcZ
    PTN                             [[:lower:]]{1,}Z
    IS_MATCH                        1
    
    TXT                             abcz
    PTN                             [[:lower:]]{1,}z
    IS_MATCH                        1
    
    TXT                             abcz
    PTN                             [[:lower:]]*z
    IS_MATCH                        1
    
    TXT                             abcz
    PTN                             [[:lower:]]+z
    IS_MATCH                        1
    
    TXT                             aggagg
    PTN                             ([[:lOwEr:]]{1}gg){2,}
    IS_MATCH                        1
    
    TXT                             aggagg
    PTN                             ([[:lOWeR:]]{1,}gg){2,}
    IS_MATCH                        1
    
    TXT                             aggagg
    PTN                             (a{1}gg){2}
    IS_MATCH                        1
    
    TXT                             aggagg
    PTN                             (a{0,}gg){2}
    IS_MATCH                        1
    
    TXT                             aggagg
    PTN                             (a{1}__){2}
    IS_MATCH                        1
    
    TXT                             aggagg
    PTN                             (a{1}__){1,}
    IS_MATCH                        1
    
    TXT                             aggagg
    PTN                             (a{1}[b-z]{2}){2}
    IS_MATCH                        1
    
    TXT                             XabaXa
    PTN                             ([X](a|b){1,3}){2}
    IS_MATCH                        1
    
    TXT                             XabaXaba
    PTN                             ([X](a|b){3}){2}
    IS_MATCH                        1
    
    TXT                             XabaX
    PTN                             ([X](a|b){0,3}){1,}
    IS_MATCH                        1
    
    TXT                             XabaX
    PTN                             ([X](a|b){0,3}){2}
    IS_MATCH                        1
    
    TXT                             XaX
    PTN                             ([X](a){0,1}){2}
    IS_MATCH                        1
    
    TXT                             XaXa
    PTN                             ([X](a){1}){2}
    IS_MATCH                        1
    
    TXT                             XaXa
    PTN                             ([X]a{1}){2}
    IS_MATCH                        1
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

