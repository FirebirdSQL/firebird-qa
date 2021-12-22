#coding:utf-8
#
# id:           functional.gtcs.parser_comments_in_sql
# title:        GTCS/tests/CF_ISQL_19. Check for problems with comments (single-line and multi-line)
# decription:   
#               	::: NB ::: 
#               	### Name of original test has no any relation with actual task of this test: ###
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_19.script
#               
#                   bug #781610 problems with one line comments (--)
#               
#                   Checked on: 4.0.0.1803 SS; 3.0.6.33265 SS; 2.5.9.27149 SC.
#                
# tracker_id:   
# min_versions: ['2.5.0']
# versions:     2.5
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.5
# resources: None

substitutions_1 = [('=', ''), ('[ \t]+', ' ')]

init_script_1 = """"""

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set heading off;

    create table test (n integer);
    insert into test values (1);

    -- I am a comment

    /* BEGIN */
    -- I am a comment
    select * from test;
    /* END */

    /* BEGIN */
    -- comment with unclosed 'quoted string
    select * from test;
    /* END */

    /* BEGIN */
    -- comment with unclosed "quoted string
    select * from test;
    /* END */

    /* BEGIN */
    -- I am a comment;
    select * from test;
    /* END */

    /* BEGIN with unclosed "quoted */
    -- I am a comment;
    select * from test;
    /* END */

    select * /*
    comment
    */
    from test;

    select * 
    /* comment */
    from test;

    select * 
    -- comment
    from test;

    /*
    Comment
    */ select * from test;


    -- Added 18.03.2020
    --#################

    -- single-line comment '*/
    select * from test;

    -- single-line comment --*/
    select * from test;

    /* * / / * q'{ 
       BEGIN multi-line comment-1
       '*/
    select * from test;


    /* '' BEGIN multi-line comment-2
       '* / / *  */
    select * from test;


"""

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    1
    1
    1
    1
    1
    1
    1
    1
    1
    1
    1
    1
    1
"""

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_stdout == act_1.clean_expected_stdout

