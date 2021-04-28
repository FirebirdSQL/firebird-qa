#coding:utf-8
#
# id:           bugs.core_1122
# title:        Recursive Query bug in FB2.1
# decription:   
# tracker_id:   CORE-1122
# min_versions: []
# versions:     2.1
# qmid:         bugs.core_1122

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 2.1
# resources: None

substitutions_1 = []

init_script_1 = """
    recreate table tb_menus(
        record_id integer,
        parent_id integer,
        order_item integer not null,
        menu_name varchar(120),
        app_name varchar(80),
        menu_icon blob sub_type 0 segment size 80
    );
    commit;
    
    insert into tb_menus values (0, null, 1, 'm1', null, null);
    insert into tb_menus values (1, 0, 1, 'm1 - sub1', 'app1.exe', null);
    insert into tb_menus values (2, 0, 1, 'm1 - sub2', 'app2.exe', null);
    commit;
  """

db_1 = db_factory(sql_dialect=3, init=init_script_1)

test_script_1 = """
    set list on;
    -------------------- 1st query ------------------
    with recursive
    menus_list as (
        select
            parent_id,
            record_id,
            order_item,
            menu_name,
            app_name,
            menu_icon,
            cast('' as varchar(255)) ident
        from tb_menus
        where parent_id is null
    
        UNION ALL
    
        select
            m.parent_id,
            m.record_id,
            m.order_item,
            m.menu_name,
            m.app_name,
            m.menu_icon, -- ::: NB ::: this field was not qualified ==> parsing error in 3.0 (but not in 2.5.4 or 2.1.7)
            h.ident || ' ' as ident
        from tb_menus m
        join menus_list h on m.parent_id = h.record_id
    )
    select
        parent_id,
        record_id,
        order_item,
        (ident || menu_name) "menu name",
        app_name,
        menu_icon
    from menus_list;
    -------------------- 2nd query ------------------
    select menu_icon from tb_menus
    UNION ALL
    select menu_icon from tb_menus;
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stdout_1 = """
    PARENT_ID                       <null>
    RECORD_ID                       0
    ORDER_ITEM                      1
    menu name                       m1
    APP_NAME                        <null>
    MENU_ICON                       <null>
    PARENT_ID                       0
    RECORD_ID                       1
    ORDER_ITEM                      1
    menu name                        m1 - sub1
    APP_NAME                        app1.exe
    MENU_ICON                       <null>
    PARENT_ID                       0
    RECORD_ID                       2
    ORDER_ITEM                      1
    menu name                        m1 - sub2
    APP_NAME                        app2.exe
    MENU_ICON                       <null>

    MENU_ICON                       <null>
    MENU_ICON                       <null>
    MENU_ICON                       <null>
    MENU_ICON                       <null>
    MENU_ICON                       <null>
    MENU_ICON                       <null>
  """

@pytest.mark.version('>=2.1')
def test_1(act_1: Action):
    act_1.expected_stdout = expected_stdout_1
    act_1.execute()
    assert act_1.clean_expected_stdout == act_1.clean_stdout

