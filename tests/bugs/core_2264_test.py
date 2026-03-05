#coding:utf-8

"""
ID:          issue-2690
ISSUE:       2690
TITLE:       ALTER DOMAIN with dependencies may leave a transaction handle in inconsistent state causing segmentation faults
DESCRIPTION:
JIRA:        CORE-2264
NOTES:
    [05.03.2026] pzotov
    1. Test verifies that attempt to change domain type from int to textual will not cause problem described in the ticket.
       Presense of stored procedure with variable of such domain must PREVENT altering domain type to non-numeric.
       Error in 5.x must raise on attempt to run this SP (i.e. on 'execute procedure ...').
       On 6.x (since shared metacache started in 6.0.0.1771) error must raise on attempt to ALTER DOMAIN, i.e. *before* SP execution.
    2. The 'SET BAIL ON' switch is ignored in all 3.x ... 5.x if statements to be executed come from PIPE mechanism.
       On 6.x this is not so since 6.0.0.150 (25-nov-2023)
       See: https://github.com/FirebirdSQL/firebird/commit/a263a19a4953efd987ce00434cc186a15705c250
       "If stdin is FILE_TYPE_PIPE then we should treat it as non-interactive (#187)"
    3. Adjusted expected output which has changed since #b38046e1 ('Encapsulation of metadata cache'; 24-feb-2026 17:31:04 +0000).
       Checked on 6.0.0.1807-46797ab; 5.0.4.1780-2040071.
"""

import pytest
from firebird.qa import *

db = db_factory()

test_script = """
    set bail on;
    set list on;
    create domain dm_num int;
    set term ^;
    create or alter procedure sp_test as
        declare v dm_num;
    begin
        v = v + v;
    end
    ^
    set term ;^
    commit;
    select 'Point-0' as msg from rdb$database;
    alter domain dm_num type varchar(11);
    select 'Point-1' as msg from rdb$database;
    alter domain dm_num type varchar(11); -- segmentation fault here
    select 'Point-2' as msg from rdb$database;
    execute procedure sp_test;
    select 'Point-3' as msg from rdb$database;
"""
substitutions = [('[ \t]+', ' ')]
act = isql_act('db', test_script, substitutions = substitutions)

@pytest.mark.version('>=3.0')
def test_1(act: Action):
    expected_stdout_5x = """
        MSG                             Point-0
        MSG                             Point-1
        MSG                             Point-2
        Statement failed, SQLSTATE = 2F000
        expression evaluation not supported
        -Error while parsing procedure SP_TEST's BLR
        MSG                             Point-3
    """

    # ::: NB ::: Since 6.0.0.150 (25-nov-2023) requirement to stop execution on 1st error ('SET BAIL ON')
    # is TAKEN IN ACCOUNT (i.e. NOT ignored as before) when running statements via PIPE.
    # See: https://github.com/FirebirdSQL/firebird/commit/a263a19a4953efd987ce00434cc186a15705c250
    # If stdin is FILE_TYPE_PIPE then we should treat it as non-interactive (#187)
    # https://github.com/FirebirdSQL/firebird/pull/187
    #
    expected_stdout_6x = """
        MSG                             Point-0
        Statement failed, SQLSTATE = 2F000
        expression evaluation not supported
        -Error while parsing procedure "PUBLIC"."SP_TEST"'s BLR
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.execute(combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
