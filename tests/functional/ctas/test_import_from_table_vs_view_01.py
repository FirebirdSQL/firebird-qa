#coding:utf-8

"""
ID:          n/a
ISSUE:       https://github.com/FirebirdSQL/firebird/issues/9053
TITLE:       CTAS. Check equality of outcomes for import data from joined TABLES vs from VIEW (that has appropriate query to same tables).
DESCRIPTION:
NOTES:
    [04.07.2026] pzotov
    Incorrect result was observed for this case when CTAS functionality has been tested in HQbird-5.x: all five rows did contain same
    values in the name_* columns ('Ref-1. Name #21' in name_1; 'Ref-2. Name #22' in name_2; ... ; 'Ref-5. Name #25' in name_5).
    See letters to Vlad and Alexey Kovyazin since 21.10.2025 1244, mailbox: 'pz@ibase.ru'.
    Checked on 6.0.0.2050-a4fa0b9.
"""
import pytest
from firebird.qa import *

db = db_factory()

substitutions = [('[ \t]+', ' ')]
act = isql_act('db', substitutions = substitutions)

@pytest.mark.version('>=6.0')
def test_1(act: Action):
    test_script = f"""
        set bail on;
        set list on;
        set autoddl off;
        recreate sequence g;
        commit;

        recreate table tdata(id int generated always as identity, pid_1 int, pid_2 int, pid_3 int, pid_4 int, pid_5 int, constraint tdata_pk primary key (id));
        recreate table tref1(id int primary key using index tref1_pk, name varchar(20));
        recreate table tref2(id int primary key using index tref2_pk, name varchar(20));
        recreate table tref3(id int primary key using index tref3_pk, name varchar(20));
        recreate table tref4(id int primary key using index tref4_pk, name varchar(20));
        recreate table tref5(id int primary key using index tref5_pk, name varchar(20));

        set term ^;
        execute block as
            declare n int = 5;
            declare pid_1 int;
            declare pid_2 int;
            declare pid_3 int;
            declare pid_4 int;
            declare pid_5 int;
        begin
            while (n > 0) do
            begin
                insert into tdata(pid_1, pid_2, pid_3, pid_4, pid_5)
                values( gen_id(g,1), gen_id(g,1), gen_id(g,1), gen_id(g,1), gen_id(g,1))
                returning pid_1, pid_2, pid_3, pid_4, pid_5 into pid_1, pid_2, pid_3, pid_4, pid_5
                ;
                n = n - 1;
                update or insert into tref1(id, name)
                values(:pid_1, 'Ref-1. Name #' || :pid_1)
                matching(id)
                ;
                update or insert into tref2(id, name)
                values(:pid_2, 'Ref-2. Name #' || :pid_2)
                matching(id)
                ;
                update or insert into tref3(id, name)
                values(:pid_3, 'Ref-3. Name #' || :pid_3)
                matching(id)
                ;
                update or insert into tref4(id, name)
                values(:pid_4, 'Ref-4. Name #' || :pid_4)
                matching(id)
                ;
                update or insert into tref5(id, name)
                values(:pid_5, 'Ref-5. Name #' || :pid_5)
                matching(id)
                ;
           end

        end
        ^
        set term ;^
        --commit;
        alter table tdata
            add constraint tdata_ref1 foreign key(pid_1) references tref1 on delete cascade
           ,add constraint tdata_ref2 foreign key(pid_2) references tref2 on delete cascade
           ,add constraint tdata_ref3 foreign key(pid_3) references tref3 on delete cascade
           ,add constraint tdata_ref4 foreign key(pid_4) references tref4 on delete cascade
           ,add constraint tdata_ref5 foreign key(pid_5) references tref5 on delete cascade
        ;

        create or alter view v_all_data as
        select
             d.id
            ,r1.name as name_1
            ,r2.name as name_2
            ,r3.name as name_3
            ,r4.name as name_4
            ,r5.name as name_5
        from tdata d
        join tref1 r1 on d.pid_1 = r1.id
        join tref2 r2 on d.pid_2 = r2.id
        join tref3 r3 on d.pid_3 = r3.id
        join tref4 r4 on d.pid_4 = r4.id
        join tref5 r5 on d.pid_5 = r5.id
        ;

        create table import_all_data_from_tabs as (
            select
                 d.id
                ,r1.name as name_1
                ,r2.name as name_2
                ,r3.name as name_3
                ,r4.name as name_4
                ,r5.name as name_5
            from tdata d
            join tref1 r1 on d.pid_1 = r1.id
            join tref2 r2 on d.pid_2 = r2.id
            join tref3 r3 on d.pid_3 = r3.id
            join tref4 r4 on d.pid_4 = r4.id
            join tref5 r5 on d.pid_5 = r5.id
        ) with data;

        create table import_all_data_from_view as (select * from v_all_data) with data;

        set count on;
        select * from import_all_data_from_tabs
        UNION DISTINCT
        select * from import_all_data_from_view;
    """

    act.expected_stdout = """
        ID 1
        NAME_1 Ref-1. Name #1
        NAME_2 Ref-2. Name #2
        NAME_3 Ref-3. Name #3
        NAME_4 Ref-4. Name #4
        NAME_5 Ref-5. Name #5
        ID 2
        NAME_1 Ref-1. Name #6
        NAME_2 Ref-2. Name #7
        NAME_3 Ref-3. Name #8
        NAME_4 Ref-4. Name #9
        NAME_5 Ref-5. Name #10
        ID 3
        NAME_1 Ref-1. Name #11
        NAME_2 Ref-2. Name #12
        NAME_3 Ref-3. Name #13
        NAME_4 Ref-4. Name #14
        NAME_5 Ref-5. Name #15
        ID 4
        NAME_1 Ref-1. Name #16
        NAME_2 Ref-2. Name #17
        NAME_3 Ref-3. Name #18
        NAME_4 Ref-4. Name #19
        NAME_5 Ref-5. Name #20
        ID 5
        NAME_1 Ref-1. Name #21
        NAME_2 Ref-2. Name #22
        NAME_3 Ref-3. Name #23
        NAME_4 Ref-4. Name #24
        NAME_5 Ref-5. Name #25

        Records affected: 5
    """
    act.isql(switches = ['-q'], input = test_script, combine_output = True)
    assert act.clean_stdout == act.clean_expected_stdout
