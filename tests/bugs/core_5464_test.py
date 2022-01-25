#coding:utf-8

"""
ID:          issue-5734
ISSUE:       5734
TITLE:       AV in fbclient when reading blob stored in incompatible encoding
DESCRIPTION:
JIRA:        CORE-5464
"""

import pytest
from firebird.qa import *

init_script = """
    create domain d_int int;
    comment on domain d_int is
    '*Лев Николаевич Толстой * *Анна Каренина * /Мне отмщение, и аз воздам/ *ЧАСТЬ ПЕРВАЯ* *I *
    Все счастливые семьи похожи друг на друга, каждая несчастливая
    семья несчастлива по-своему.
    Все смешалось в доме Облонских. Жена узнала, что муж был в связи
    с бывшею в их доме француженкою-гувернанткой, и объявила мужу, что
    не может жить с ним в одном доме. Положение это продолжалось уже
    третий день и мучительно чувствовалось и самими супругами, и всеми
    членами семьи, и домочадцами. Все члены семьи и домочадцы
    чувствовали, что нет смысла в их сожительстве и что на каждом
    п1
    ';
    commit;
"""

db_1 = db_factory(charset='WIN1251', init=init_script)

test_script = """
    set blob all;
    set list on;

    select c.rdb$character_set_name as connection_cset, r.rdb$character_set_name as db_default_cset
    from mon$attachments a
    join rdb$character_sets c on a.mon$character_set_id = c.rdb$character_set_id
    cross join rdb$database r where a.mon$attachment_id=current_connection;

    select rdb$field_name, rdb$system_flag, rdb$description
    from rdb$fields where rdb$description is not null;
"""

act = isql_act('db_1', test_script)

expected_stdout = """
    CONNECTION_CSET                 WIN1250
    DB_DEFAULT_CSET                 WIN1251
"""

expected_stderr = """
    Statement failed, SQLSTATE = 22018
    Cannot transliterate character between character sets
"""

@pytest.mark.version('>=3.0.2')
def test_1(act: Action):
    act.expected_stderr = expected_stderr
    act.expected_stdout = expected_stdout
    act.isql(switches=['-q'], input=test_script, charset='WIN1250')
    assert (act.clean_stderr == act.clean_expected_stderr and
            act.clean_stdout == act.clean_expected_stdout)
