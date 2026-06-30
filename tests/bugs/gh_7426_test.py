#coding:utf-8

"""
ID:          issue-7426
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/7426
TITLE:       Ensure the DDL trigger requests are cached
DESCRIPTION:
    Test prepares trace config with requrement to see statements start / finish and TRIGGERS compilation.
    We create several DB objects, including DDL for 'BEFORE ANY DDL' and'AFTER ANY DDL'.
    Finally, we parse trace log and filter only interesting lines matching to set of allowed_patterns.

    Before this ticked was fixed, every time we did some DDL appropriate trigger was compiled
    and this could be seen in a trace log (checked on 5.0.0.1182).
    No errors must present in the trace log.
NOTES:
    [07-sep-2023] pzotov
        1. The term 'COMPILE' means parsing of BLR code into an execution tree, i.e. this action
           occurs when unit code is loaded into metadata cache. 
           Explained by dimitr, 17.08.2023 16:30 (email, subj: "COMPILE trace events for procedures/functions/...")
        2. Currently there is no way to specify in the trace what EXACT type of DDL trigger fired.
           It is shown as "AFTER DDL".
    [30.06.2026] pzotov
        Prior feature (of this ticket) was implemented, triggers TRG_ANY_DDL_STATEMENT_BEFORE + _AFTER have
        fired on *every* DDL statement.
        Trace contained three COMPILE_TRIGGER blocks for every DDL, e.g. (for snapshot 5.0.0.1182):
            EXECUTE_STATEMENT_START
            create function /* trace_me */ fn_test returns dm_test as begin return (select count(*) from v_test); end
            COMPILE_TRIGGER
            Trigger TRG_CREATE_FUNCTION_BEFORE (BEFORE DDL): <<<<<<<<<<<<<<< [ 1 ]
            COMPILE_TRIGGER
            Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL): <<<<<<<<<<<<< [ 2 ]
            COMPILE_TRIGGER
            Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL): <<<<<<<<<<<<<<< [ 3 ]
            EXECUTE_STATEMENT_FINISH
            create function /* trace_me */ fn_test returns dm_test as begin return (select count(*) from v_test); end
        After feature was implemented trace has only one occurrence of 'COMPILE_TRIGGER' and looks like this (5.0.0.1190):
            EXECUTE_STATEMENT_START
            create function /* trace_me */ fn_test returns dm_test as begin return (select count(*) from v_test); end
            COMPILE_TRIGGER
            Trigger TRG_CREATE_FUNCTION_BEFORE (BEFORE DDL):
            EXECUTE_STATEMENT_FINISH
            create function /* trace_me */ fn_test returns dm_test as begin return (select count(*) from v_test); end
        Since shared metacache was introduced (6.0.0.1771) the order of AFTER_DDL trigger appearance changed but the number
        of its occurences remained the same:
           6.0.0.1465:
               Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
               Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
               Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
           6.0.0.1771:
               Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
               Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
               Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        The reason of this: "when changing the set of triggers, the entire set (in this case DB_TRIGGER_DDL) is reloaded."
        Explained by Alex, 30.06.2026 09:08
"""
import locale
import re
import pytest
from firebird.qa import *

db = db_factory()

act = python_act('db')

trace = ['log_initfini = false',
         'log_errors = true',
         'time_threshold = 0',
         'include_filter = "%trace_me%"',
         'log_statement_start = true',
         'log_statement_finish = true',
         'log_trigger_compile = true',
         ]

allowed_patterns = [ ' ERROR AT ', '.*trace_me.*', 'EXECUTE_STATEMENT_START', 'EXECUTE_STATEMENT_FINISH', 'COMPILE_TRIGGER', 'Trigger\\s+.*TRG_.*', ]
allowed_patterns = [ re.compile(r, re.IGNORECASE) for r in allowed_patterns]

@pytest.mark.trace
@pytest.mark.version('>=5.0')
def test_1(act: Action, capsys):

    TRACE_TAG = '/* trace_me */'
    sttm_lst = (
        f'create trigger {TRACE_TAG} trg_any_ddl_statement_after active after any ddl statement as begin end',
        f'create trigger {TRACE_TAG} trg_any_ddl_statement_before active before any ddl statement as begin end',

        f'create trigger {TRACE_TAG} trg_create_sequence_before active before CREATE SEQUENCE as begin end',
        f'create trigger {TRACE_TAG} trg_create_exception_before active before CREATE EXCEPTION as begin end',
        f'create trigger {TRACE_TAG} trg_create_collation_before active before CREATE COLLATION as begin end',
        f'create trigger {TRACE_TAG} trg_create_domain_before active before CREATE DOMAIN as begin end',
        f'create trigger {TRACE_TAG} trg_create_table_before active before CREATE TABLE as begin end',
        f'create trigger {TRACE_TAG} trg_create_view_before active before CREATE VIEW as begin end',
        f'create trigger {TRACE_TAG} trg_create_proc_before active before CREATE PROCEDURE as begin end',
        f'create trigger {TRACE_TAG} trg_create_function_before active before CREATE FUNCTION as begin end',

        f'create sequence {TRACE_TAG} g',
        f"create exception {TRACE_TAG} exc_test 'boo!'",
        f"create collation pt_pt2 for iso8859_1 from pt_pt '{'SPECIALS-FIRST=1'.upper()}'",
        f'create domain {TRACE_TAG} dm_test int',
        f'create table {TRACE_TAG} test(x dm_test)',
        f'create view {TRACE_TAG} v_test as select * from test',
        f'create procedure {TRACE_TAG} sp_test returns(o_x dm_test) as begin for select x from v_test into o_x do suspend; end',
        f'create function {TRACE_TAG} fn_test returns dm_test as begin return (select count(*) from v_test); end',
    )

    with act.trace(db_events=trace, encoding = locale.getpreferredencoding(), encoding_errors='utf8'):
        with act.db.connect() as con:
            for s in sttm_lst:
                con.execute_immediate(s)
                con.commit() # mandatory for 5.x and 6.x prior shared metacache; otherwise COMPILE_TRIGGER will not appear in the trace

    # Process trace
    for line in act.trace_log:
        if line.split():
            for p in allowed_patterns:
                if ( s := p.search(line) ):
                    print(s.group())
                    break # some line of trace can match 2+ patterns, eg: '.*trace_me.*' and 'Trigger\s+.*TRG_.*'

    expected_stdout_5x = f"""
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_any_ddl_statement_after active after any ddl statement as begin end
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_any_ddl_statement_after active after any ddl statement as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_any_ddl_statement_before active before any ddl statement as begin end
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_any_ddl_statement_before active before any ddl statement as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_sequence_before active before CREATE SEQUENCE as begin end
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_sequence_before active before CREATE SEQUENCE as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_exception_before active before CREATE EXCEPTION as begin end
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_exception_before active before CREATE EXCEPTION as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_collation_before active before CREATE COLLATION as begin end
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_collation_before active before CREATE COLLATION as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_domain_before active before CREATE DOMAIN as begin end
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_domain_before active before CREATE DOMAIN as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_table_before active before CREATE TABLE as begin end
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_table_before active before CREATE TABLE as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_view_before active before CREATE VIEW as begin end
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_view_before active before CREATE VIEW as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_proc_before active before CREATE PROCEDURE as begin end
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_proc_before active before CREATE PROCEDURE as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_function_before active before CREATE FUNCTION as begin end
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_function_before active before CREATE FUNCTION as begin end
        EXECUTE_STATEMENT_START
        create sequence /* trace_me */ g
        COMPILE_TRIGGER
        Trigger TRG_CREATE_SEQUENCE_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_BEFORE (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger TRG_ANY_DDL_STATEMENT_AFTER (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create sequence /* trace_me */ g
        EXECUTE_STATEMENT_START
        create exception /* trace_me */ exc_test 'boo!'
        COMPILE_TRIGGER
        Trigger TRG_CREATE_EXCEPTION_BEFORE (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create exception /* trace_me */ exc_test 'boo!'
        COMPILE_TRIGGER
        Trigger TRG_CREATE_COLLATION_BEFORE (BEFORE DDL):
        EXECUTE_STATEMENT_START
        create domain /* trace_me */ dm_test int
        COMPILE_TRIGGER
        Trigger TRG_CREATE_DOMAIN_BEFORE (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create domain /* trace_me */ dm_test int
        EXECUTE_STATEMENT_START
        create table /* trace_me */ test(x dm_test)
        COMPILE_TRIGGER
        Trigger TRG_CREATE_TABLE_BEFORE (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create table /* trace_me */ test(x dm_test)
        EXECUTE_STATEMENT_START
        create view /* trace_me */ v_test as select * from test
        COMPILE_TRIGGER
        Trigger TRG_CREATE_VIEW_BEFORE (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create view /* trace_me */ v_test as select * from test
        EXECUTE_STATEMENT_START
        create procedure /* trace_me */ sp_test returns(o_x dm_test) as begin for select x from v_test into o_x do suspend; end
        COMPILE_TRIGGER
        Trigger TRG_CREATE_PROC_BEFORE (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create procedure /* trace_me */ sp_test returns(o_x dm_test) as begin for select x from v_test into o_x do suspend; end
        EXECUTE_STATEMENT_START
        create function /* trace_me */ fn_test returns dm_test as begin return (select count(*) from v_test); end
        COMPILE_TRIGGER
        Trigger TRG_CREATE_FUNCTION_BEFORE (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create function /* trace_me */ fn_test returns dm_test as begin return (select count(*) from v_test); end
    """

    expected_stdout_6x = f"""
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_any_ddl_statement_after active after any ddl statement as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_any_ddl_statement_after active after any ddl statement as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_any_ddl_statement_before active before any ddl statement as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_any_ddl_statement_before active before any ddl statement as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_sequence_before active before CREATE SEQUENCE as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_sequence_before active before CREATE SEQUENCE as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_exception_before active before CREATE EXCEPTION as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_exception_before active before CREATE EXCEPTION as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_collation_before active before CREATE COLLATION as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_collation_before active before CREATE COLLATION as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_domain_before active before CREATE DOMAIN as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_domain_before active before CREATE DOMAIN as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_table_before active before CREATE TABLE as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_table_before active before CREATE TABLE as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_view_before active before CREATE VIEW as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_view_before active before CREATE VIEW as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_proc_before active before CREATE PROCEDURE as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_proc_before active before CREATE PROCEDURE as begin end
        EXECUTE_STATEMENT_START
        create trigger /* trace_me */ trg_create_function_before active before CREATE FUNCTION as begin end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_AFTER" (AFTER DDL):
        EXECUTE_STATEMENT_FINISH
        create trigger /* trace_me */ trg_create_function_before active before CREATE FUNCTION as begin end
        EXECUTE_STATEMENT_START
        create sequence /* trace_me */ g
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_CREATE_SEQUENCE_BEFORE" (BEFORE DDL):
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_ANY_DDL_STATEMENT_BEFORE" (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create sequence /* trace_me */ g
        EXECUTE_STATEMENT_START
        create exception /* trace_me */ exc_test 'boo!'
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_CREATE_EXCEPTION_BEFORE" (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create exception /* trace_me */ exc_test 'boo!'
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_CREATE_COLLATION_BEFORE" (BEFORE DDL):
        EXECUTE_STATEMENT_START
        create domain /* trace_me */ dm_test int
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_CREATE_DOMAIN_BEFORE" (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create domain /* trace_me */ dm_test int
        EXECUTE_STATEMENT_START
        create table /* trace_me */ test(x dm_test)
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_CREATE_TABLE_BEFORE" (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create table /* trace_me */ test(x dm_test)
        EXECUTE_STATEMENT_START
        create view /* trace_me */ v_test as select * from test
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_CREATE_VIEW_BEFORE" (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create view /* trace_me */ v_test as select * from test
        EXECUTE_STATEMENT_START
        create procedure /* trace_me */ sp_test returns(o_x dm_test) as begin for select x from v_test into o_x do suspend; end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_CREATE_PROC_BEFORE" (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create procedure /* trace_me */ sp_test returns(o_x dm_test) as begin for select x from v_test into o_x do suspend; end
        EXECUTE_STATEMENT_START
        create function /* trace_me */ fn_test returns dm_test as begin return (select count(*) from v_test); end
        COMPILE_TRIGGER
        Trigger "PUBLIC"."TRG_CREATE_FUNCTION_BEFORE" (BEFORE DDL):
        EXECUTE_STATEMENT_FINISH
        create function /* trace_me */ fn_test returns dm_test as begin return (select count(*) from v_test); end
    """

    act.expected_stdout = expected_stdout_5x if act.is_version('<6') else expected_stdout_6x
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
