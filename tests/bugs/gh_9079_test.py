#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9079
TITLE:       Wrong cursor ID for the second query in the procedure during profiling
DESCRIPTION:
    We filter out all rows from plg$prof_record_sources except those that contain text 'Select Expression (line N, column M)'.
    Then we count distinct values of CURSOR_ID and check that this value is 2.
    The name of profiling session ('manual nested loop') is stored in context variable in order to avoid duplicates.
NOTES:
    [02.07.2026] pzotov
    Confirmed bug on 6.0.0.2050-09246e5.
    Checked on 6.0.0.2050-a4fa0b9 -- all fine.
"""
import os
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):

    SCHEMA_SEARCH_STTM = '' if act.is_version('<6') else 'set search_path to PLG$PROFILER, PUBLIC;'
    null_dev = os.devnull

    test_script = f"""
        set list on;
        {SCHEMA_SEARCH_STTM}

        recreate table clients
        (
            client_id   int primary key,
            client_name varchar(20)
        );

        recreate table orders
        (
            order_id     int,  
            client_id    int
        );
        commit;

        insert into clients (client_id, client_name) values (1, 'client_1');
        insert into clients (client_id, client_name) values (2, 'client_2');
        insert into orders(order_id, client_id) values(1, 1);
        commit;

        set term ^;
        create or alter procedure manual_join
        returns (
            order_id    type of column orders.order_id,
            client_id   type of column clients.client_id,
            client_name type of column clients.client_name
        )
        as begin
            for select order_id, client_id
            from orders
            into
                :order_id,
                :client_id
            do begin
                for
                    select client_name
                    from clients c
                    where c.client_id = :client_id
                    into :client_name
                do begin
                    suspend;
                end
            end
        end
        ^
        execute block as
        begin
            rdb$set_context('USER_SESSION', 'PROFILER_SESSION_NAME', 'manual nested loop');
        end
        ^
        set term ;^
        commit;

        out {null_dev};
        select rdb$profiler.start_session( rdb$get_context('USER_SESSION', 'PROFILER_SESSION_NAME') , null, null, null, null) from rdb$database;
        select * from manual_join;
        execute procedure rdb$profiler.finish_session;
        commit;
        out;

        select count(distinct rs.cursor_id) as cur_id_distinct_count
        from plg$prof_record_sources rs
        join plg$prof_sessions ps using(profile_id)
        where
            ps.description = rdb$get_context('USER_SESSION', 'PROFILER_SESSION_NAME')
            and rs.access_path similar to '%line [[:DIGIT:]]+% col(umn)? [[:DIGIT:]]+%'
        ;

    """

    act.expected_stdout = """
        CUR_ID_DISTINCT_COUNT 2
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
