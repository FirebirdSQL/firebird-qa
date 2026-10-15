#coding:utf-8

"""
ID:          b383b90278
ISSUE:       https://www.sqlite.org/src/tktview/b383b90278
TITLE:       Assertion in UPDATE statement for textual column which has check constraint that involves numeric comparison
DESCRIPTION:
NOTES:
    [15.08.2025] pzotov
        SQL schema name (introduced since 6.0.0.834), single and double quotes are suppressed in the output.
        See $QA_HOME/README.substitutions.md or https://github.com/FirebirdSQL/firebird-qa/blob/master/README.substitutions.md
        Checked on 6.0.0.1204, 5.0.4.1701, 4.0.7.3231, 3.0.14.33824
    [15.10.2026] pzotov
    Adjusted code to be performed in 6.x since introducing non-decimal integer literals, see:
    See notes in https://github.com/FirebirdSQL/firebird/pull/8564#issue-3059832235
        0x0 to 0x7FFFFFFFFF are positive INTEGER numbers with values from 0 to 2147483647
        0x80000000 to 0x7FFFFFFFFFFFFFFF are positive BIGINT numbers with values from 2147483648 to 9223372036854775807.
        0x8000000000000000 to 0x7FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF are positive INT128 numbers with values from 9223372036854775808 to 170141183460469231731687303715884105727

    NEGATIVE hex value thast must violate CHECK constraint is depending now on FB version, see `NEGATIVE_HEX_LITERAL`.
    Checked on 6.0.0.2211 5.0.5.1906 4.0.8.3328 3.0.15.33890
"""

import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]

# QA_GLOBALS -- dict, is defined in qa/plugin.py, obtain settings
# from act.files_dir/'test_config.ini':
#
addi_subst_settings = QA_GLOBALS['schema_n_quotes_suppress']
addi_subst_tokens = addi_subst_settings['addi_subst']

for p in addi_subst_tokens.split(' '):
    substitutions.append( (p, '') )

act = python_act('db', substitutions = substitutions)

@pytest.mark.version('>=3')
def test_1(act: Action):

    NEGATIVE_HEX_LITERAL = '0xF0000000' if act.is_version('<6') else '-0xF0000000'
    test_script = f"""
        set list on;
        create table test(
            f01 varchar(20)
            ,constraint test_chk check( f01 between 0 and cast(f01 as int) )
        );
        insert into test values (0);

        set count on;
        -- arithmetic exception, numeric overflow / -numeric value is out of range:
        update test set f01 = '2147483648';

        -- must raise " Operation violates CHECK constraint...":
        update test set f01 = -10;

        -- must raise conversion error:
        update test set f01 = 'false';

        -- must raise " Operation violates CHECK constraint..." because
        -- 0xF0000000 is -268435456, see doc/sql.extensions/README.hex_literals.txt
        update test set f01 = {NEGATIVE_HEX_LITERAL};
    """

    expected_stdout = """
        Statement failed, SQLSTATE = 22003
        arithmetic exception, numeric overflow, or string truncation
        -numeric value is out of range
        -At trigger 'CHECK_2'
        Records affected: 0

        Statement failed, SQLSTATE = 23000
        Operation violates CHECK constraint TEST_CHK on view or table TEST
        -At trigger 'CHECK_2'
        Records affected: 0

        Statement failed, SQLSTATE = 22018
        conversion error from string "false"
        -At trigger 'CHECK_2'
        Records affected: 0

        Statement failed, SQLSTATE = 23000
        Operation violates CHECK constraint TEST_CHK on view or table TEST
        -At trigger 'CHECK_2'
        Records affected: 0
    """

    act.expected_stdout = expected_stdout
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
