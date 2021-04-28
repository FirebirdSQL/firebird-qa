#coding:utf-8
#
# id:           bugs.core_4160
# title:        Parameterized exception does not accept not ASCII characters as parameter
# decription:   
# tracker_id:   CORE-4160
# min_versions: ['3.0']
# versions:     3.0
# qmid:         None

import pytest
from firebird.qa import db_factory, isql_act, Action

# version: 3.0
# resources: None

substitutions_1 = [('-At procedure.*', '')]

init_script_1 = """
    create or alter procedure sp_alert(a_lang char(2), a_new_amount int) as begin end;
    commit;
    recreate exception ex_negative_remainder ' @1 (@2)';
    commit;
  """

db_1 = db_factory(page_size=4096, charset='UTF8', sql_dialect=3, init=init_script_1)

test_script_1 = """
    set term ^;
    create or alter procedure sp_alert(a_lang char(2), a_new_amount int) as
    begin
       if (a_lang = 'cz') then
         exception ex_negative_remainder using ('Czech: New Balance bude menší než nula', a_new_amount);
       else	if (a_lang = 'pt') then
         exception ex_negative_remainder using ('Portuguese: New saldo será menor do que zero', a_new_amount);
       else	if (a_lang = 'dm') then
         exception ex_negative_remainder using ('Danish: New Balance vil være mindre end nul', a_new_amount);
       else	if (a_lang = 'gc') then
         exception ex_negative_remainder using ('Greek: Νέα ισορροπία θα είναι κάτω από το μηδέν', a_new_amount);
       else	if (a_lang = 'fr') then
         exception ex_negative_remainder using ('French: Nouveau solde sera inférieur à zéro', a_new_amount);
       else
         exception ex_negative_remainder using ('Russian: Новый остаток будет меньше нуля', a_new_amount);
    end
    ^
    set term ;^
    commit;
    execute procedure sp_alert('cz', -1);
    execute procedure sp_alert('pt', -2);
    execute procedure sp_alert('dm', -3);
    execute procedure sp_alert('gc', -4);
    execute procedure sp_alert('fr', -5);
    execute procedure sp_alert('jp', -6);
  """

act_1 = isql_act('db_1', test_script_1, substitutions=substitutions_1)

expected_stderr_1 = """
    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_NEGATIVE_REMAINDER
    - Czech: New Balance bude menší než nula (-1)

    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_NEGATIVE_REMAINDER
    - Portuguese: New saldo será menor do que zero (-2)

    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_NEGATIVE_REMAINDER
    - Danish: New Balance vil være mindre end nul (-3)

    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_NEGATIVE_REMAINDER
    - Greek: Νέα ισορροπία θα είναι κάτω από το μηδέν (-4)

    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_NEGATIVE_REMAINDER
    - French: Nouveau solde sera inférieur à zéro (-5)

    Statement failed, SQLSTATE = HY000
    exception 1
    -EX_NEGATIVE_REMAINDER
    - Russian: Новый остаток будет меньше нуля (-6)
  """

@pytest.mark.version('>=3.0')
def test_1(act_1: Action):
    act_1.expected_stderr = expected_stderr_1
    act_1.execute()
    assert act_1.clean_expected_stderr == act_1.clean_stderr

