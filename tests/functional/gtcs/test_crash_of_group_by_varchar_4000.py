#coding:utf-8
#
# id:           functional.gtcs.crash_of_group_by_varchar_4000
# title:        GTCS/tests/CF_ISQL_33. Crash on attempt to GROUP BY on table with varchar(4000) field
# decription:   
#               	::: NB ::: 
#               	### Name of original test has no any relation with actual task of this test: ###
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_33.script
#               
#                   Source description (dominikfaessler, message of 2004-05-27 13:11:09; FB 1.5.1.4443):
#                   https://sourceforge.net/p/firebird/mailman/message/17071981/
#               
#                   Issue in original test:
#                   bug #961543 Server Crash ISO8859_1 and DE_DE
#               
#                   Checked on: 4.0.0.1804 SS; 3.0.6.33271 SS; 2.5.9.27149 SC.
#                   NB: it is enough in 'expected_stdout' to show only name of resulting field ('F01')
#                   rather than the whole output.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('[ \t]+', ' '), ('^((?!F01|Records affected).)*$', '')]

init_script_1 = """"""

db_1 = db_factory(charset='ISO8859_1', sql_dialect=3, init=init_script_1)

test_script_1 = """
    CREATE TABLE SNIPPETS (
    f01 VARCHAR(4000) COLLATE DE_DE
    );

    SET TERM ^;

    insert into snippets values('
    function JsShowZeroFilled(inValue) {
    if(inValue > 9) {
    return inValue;
    } else {
    return ''0'' + inValue;
    }
    }




    function JsGetWochentagname(wochentag,wochentagtyp,langcode) {
    var wochentagname;


    array_DE = new Array("SO,Son.,Sonntag", "MO,Mon.,Montag",
    "DI,Di.,Dienstag", "MI,Mi.,Mittwoch",
    "DO,Don.,Donnerstag","FR,Fr.,Freitag", "SA,Sam.,Samstag");
    array_EN = new Array("SU,Su.,Sunday", "MO,Mon.,Monday",
    "TU,Tu.,Tuesday", "WE,We.,Wednesday", "DO,Th.,Thursday",
    "FR,Fr.,Friday", "SA,Sa.,Saturday");


    if (langcode.toUpperCase() == ''DE'') {
    array_wochentagname = array_DE[wochentag].split('','');
    wochentagname = array_wochentagname[wochentagtyp-1];
    } else {
    array_wochentagname = array_EN[wochentag].split('','');
    wochentagname = array_wochentagname[wochentagtyp-1];
    }
    return wochentagname;
    }
    ')
    ^
    set term ;^
    commit;

    set count on;
    set list on;
    select f01 from snippets group by f01;


  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    F01
    Records affected: 1
  """

@pytest.mark.version('>=2.5')
def test_crash_of_group_by_varchar_4000_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

