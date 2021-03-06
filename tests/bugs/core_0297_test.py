#coding:utf-8
#
# id:           bugs.core_0297
# title:        bug #585624 IB server stalled by simple script
# decription:   
#               	::: NB ::: 
#               	### Name of original test has no any relation with actual task of this test: ###
#                   https://github.com/FirebirdSQL/fbtcs/blob/master/GTCS/tests/CF_ISQL_23.script
#               
#                   Issue in original script: bug #585624 IB server stalled by simple script"
#                   Found in FB tracker as: http://tracker.firebirdsql.org/browse/CORE-297
#                   Fixed in 1.5.0
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

db_1 = db_factory(charset='ISO8859_1', sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create procedure group_copy (
        source integer,
        destination integer)
    as
    begin
        exit;
    end^

    create procedure insert_values (
        cont integer,
        d_group integer)
    as
    begin
        exit;
    end^
    set term ;^

    create table groups (
        gr_id integer not null,
        gr_name varchar(40) character set iso8859_1 not null
        collate de_de
    );

    create table test (
        id integer not null,
        t_group integer not null
    );

    alter table groups add constraint pk_groups primary key (gr_id);
    alter table test add constraint pk_test primary key (id, t_group);
    alter table test add constraint fk_test foreign key (t_group) references groups (gr_id);

    set term ^;
    alter procedure group_copy (
        source integer,
        destination integer)
    as
    begin
        insert into test( id, t_group )
        select a.id, :destination
        from test a
        where a.t_group = :source
            and not exists (
                select * from test b
                where b.id = a.id
                and :destination = b.t_group
            );
    end
    ^

    alter procedure insert_values (
        cont integer,
        d_group integer)
    as
        declare anz integer;
    begin
        anz = 0;
        
        while ( anz < cont ) do
        begin
            if ( not exists (
                                select id
                                from test where id = :anz
                                and t_group = :d_group
                            )
                ) then
                insert into test( id, t_group ) values( :anz, :d_group );

            anz = anz +1;
        end
    end
    ^
    set term ;^
    commit;


    insert into groups values ( 1 , 'Group1' );
    insert into groups values ( 2 , 'Group2' );
    commit;
    execute procedure insert_values( 3000 , 1);
    commit;

    delete from test where t_group = 2;
    execute procedure group_copy( 1 , 2 );
    commit;

    set list on;
    select count(*) from test;
    select * from groups;

  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    COUNT                           6000
    GR_ID                           1
    GR_NAME                         Group1
    GR_ID                           2
    GR_NAME                         Group2
  """

@pytest.mark.version('>=2.5')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

