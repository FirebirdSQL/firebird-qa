# coding:utf-8

"""
ID:          n/a
TITLE:       INSERT or UPDATE of streamed blob must take in account appropriate user grants or such operations.
DESCRIPTION: 
    Test creates a table with blob field, temporary file with some data and non-privileged user ('tmp_user').
    Then we GRANT to this user access to select, insert and update of test table.
    User opens the file with blob data and uses it as source for STREAMED blob that is to be saved in DB,
    see 'file_with_data_for_blob'.
    No errors must occur during DML on this table ('INSERT RETURNING ...' and 'UPDATE RETURNING ...').
    After this, we REVOKE privileges from this user and repeat. Neither INSERT nor UPDATE must be allowed now.
NOTES:
    [22.04.2026] pzotov
    Based on test provided by Anton Zuev, Redbase.
    File: test_update_blob_in_table.py (ID = 'stest.Blob_Testing.updateblobidintable')
    Checked on 6.0.0.1914; 5.0.4.1813; 4.0.7.3271.
"""

from pathlib import Path
import pytest
from firebird.qa import *
from firebird.driver import DatabaseError, FirebirdWarning

TEST_TABLE = 'BLOB_STORAGE'

db = db_factory(init = f'create table {TEST_TABLE} (id int primary key, blob_fld blob); commit;')

act = python_act('db')

tmp_data = temp_file('tmp_blob.dat')
tmp_user = user_factory('db', name='tmp_blob_writer', password='456')

BLOB_DATA = """
— Eh bien, mon prince. Gênes et Lucques ne sont plus que des apanages, des поместья, de la famille Buonaparte.
Non, je vous préviens, que si vous ne me dites pas, que nous avons la guerre, si vous vous permettez encore de pallier toutes
les infamies, toutes les atrocités de cet Antichrist (ma parole, j’y crois) — je ne vous connais plus, vous n’êtes plus mon ami,
vous n’êtes plus мой верный раб, comme vous dites.
Ну, здравствуйте, здравствуйте. Je vois que je vous fais peur, садитесь и рассказывайте.
Так говорила в июле 1805 года известная Анна Павловна Шерер, фрейлина и приближенная императрицы Марии Феодоровны, встречая важного
и чиновного князя Василия, первого приехавшего на ее вечер. Анна Павловна кашляла несколько дней, у нее был грипп, как она говорила
(грипп был тогда новое слово, употреблявшееся только редкими).
"""

@pytest.mark.version('>=4.0')
def test_1(act: Action, tmp_user: User, tmp_data: Path, capsys):

    with open(tmp_data, 'w', encoding = 'utf-8') as f:
        f.write(BLOB_DATA)

    for optype in ('grant', 'revoke'):
        with act.db.connect() as con:
            if optype == 'grant':
                #####################
                ###   g r a n t   ###
                #####################
                con.execute_immediate(f"grant select,insert,update(blob_fld) on {TEST_TABLE} to {tmp_user.name}")
            else:
                ########################
                ###   r e v o k e    ###
                ########################
                con.execute_immediate(f"revoke insert on {TEST_TABLE} from {tmp_user.name}")
                con.execute_immediate(f"revoke update(blob_fld) on {TEST_TABLE} from {tmp_user.name}")
            con.commit()

        inserted_blob = updated_blob = None
        with act.db.connect(user=tmp_user.name, password=tmp_user.password, charset = 'utf8') as con:
            cur = con.cursor()
            with open(tmp_data, 'r', encoding = 'utf-8') as file_with_data_for_blob:
                try:
                    cur.execute(f"insert into {TEST_TABLE}(id, blob_fld) values (1, ?) returning blob_fld", (file_with_data_for_blob,))
                    for r in cur:
                        inserted_blob = r[0]
                    cur.execute(f"insert into {TEST_TABLE}(id, blob_fld) values (2, ?)", (None,))
                    print(f'{optype=}: INSERT streamed blob completed.')
                except DatabaseError as e:
                    print(f'{optype=}: INSERT streamed blob failed.')
                    print( e.__str__() )
                    print(e.gds_codes)

            with open(tmp_data, 'r', encoding = 'utf-8') as file_with_data_for_blob:
                try:
                    cur.execute(f"update {TEST_TABLE} set blob_fld = ? where blob_fld is null returning blob_fld", (file_with_data_for_blob,))
                    for r in cur:
                        updated_blob = r[0]
                    print(f'{optype=}: UPDATE streamed blob completed.')
                except DatabaseError as e:
                    print(f'{optype=}: UPDATE streamed blob failed.')
                    print( e.__str__() )
                    print(e.gds_codes)

            con.commit()

        if optype == 'grant':
            assert inserted_blob and inserted_blob == updated_blob
        else:
            assert not (inserted_blob or updated_blob)
    

    SQL_SCHEMA_PREFIX = '' if act.is_version('<6') else'"PUBLIC".'
    TEST_TABLE_NAME = TEST_TABLE if act.is_version('<6') else f'{SQL_SCHEMA_PREFIX}"{TEST_TABLE}"'

    expected_stdout = f"""
        optype='grant': INSERT streamed blob completed.
        optype='grant': UPDATE streamed blob completed.

        optype='revoke': INSERT streamed blob failed.
        no permission for INSERT access to TABLE {TEST_TABLE_NAME}
        -Effective user is {tmp_user.name.upper()}
        (335544352, 335545254)

        optype='revoke': UPDATE streamed blob failed.
        no permission for UPDATE access to TABLE {TEST_TABLE_NAME}
        -Effective user is {tmp_user.name.upper()}
        (335544352, 335545254)
    """
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
