#coding:utf-8
#
# id:           bugs.core_2721
# title:        Issue with SIMILAR TO and UTF8 on 2.5 Beta 2 (and 1)
# decription:   
# tracker_id:   CORE-2721
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = []

init_script_1 = """"""

db_1 = db_factory(from_backup='core2721.fbk', init=init_script_1)

test_script_1 = """
    set list on;
    set count on;
    select * from test where utf8field similar to 'DELL %';
    select * from test where utf8field similar to 'DE %';
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    ANSIFIELD                       DELL COMPUTERS
    UTF8FIELD                       DELL COMPUTERS
    UNICODECIFIELD                  DELL COMPUTERS
    
    ANSIFIELD                       DELL BV
    UTF8FIELD                       DELL BV
    UNICODECIFIELD                  DELL BV
   
    ANSIFIELD                       DELL BV-GLOBAL COMMUNITY
    UTF8FIELD                       DELL BV-GLOBAL COMMUNITY
    UNICODECIFIELD                  DELL BV-GLOBAL COMMUNITY

    Records affected: 3
    
    ANSIFIELD                       DE HEER P.W. BALFOORT
    UTF8FIELD                       DE HEER P.W. BALFOORT
    UNICODECIFIELD                  DE HEER P.W. BALFOORT
    
    ANSIFIELD                       DE DRIESTAR
    UTF8FIELD                       DE DRIESTAR
    UNICODECIFIELD                  DE DRIESTAR
    
    ANSIFIELD                       DE SINGEL
    UTF8FIELD                       DE SINGEL
    UNICODECIFIELD                  DE SINGEL
    
    ANSIFIELD                       DE BOER PLASTIK B.V.
    UTF8FIELD                       DE BOER PLASTIK B.V.
    UNICODECIFIELD                  DE BOER PLASTIK B.V.
    
    ANSIFIELD                       DE LOOT PC REPAIR
    UTF8FIELD                       DE LOOT PC REPAIR
    UNICODECIFIELD                  DE LOOT PC REPAIR
    
    ANSIFIELD                       DE HEER P.W. BALFOORT
    UTF8FIELD                       DE HEER P.W. BALFOORT
    UNICODECIFIELD                  DE HEER P.W. BALFOORT
    
    Records affected: 6
  """

@pytest.mark.version('>=2.5')
def test_core_2721_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

