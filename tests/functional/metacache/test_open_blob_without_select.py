# coding:utf-8

"""
ID:          n/a
TITLE:       Open BLOB without selection
DESCRIPTION: 
NOTES:
    [22.04.2026] pzotov
    Test has been provided by Anton Zuev, Redsoft.
    Bug existed in 6.0.0.1887-2e18929:
        1) attempt to open blob by user who *has* appropriate grant failed (on Classic) with:
            Invalid blob ID 80:0
            (335544382,)
        2) in contrary, attempt to open blob WITHOUT rights to do that completed OK:
            "Blob opened OK, hex(blob_id.low)='0x...'; hex(blob_id.high)='0x...', blob_length=N, segment_size=M"
            (while error 'no permission for ,,,' expected; this occurred both on Super and Classic)
    Fixed in #7b617a95 ("Fixed assertion reported privately...")
    Checked on 6.0.0.1891-f2367d8.
"""
import os
import pytest
from firebird.qa import *
from firebird.driver import DatabaseError, Cursor
from firebird.driver.types import BPBItem, BlobType, BlobInfoCode

db = db_factory()

substitutions = [
    ('0x\\d{1,}', '0x...'),
    ('blob_length=\\d+', 'blob_length=N'),
    ('segment_size=\\d+', 'segment_size=M'),
]
act = python_act('db', substitutions =substitutions)

tmp_user = user_factory('db', name='tmp_blob_reader', password='123')

BLOB_DATA = """— Eh bien, mon prince. Gênes et Lucques ne sont plus que des apanages, des поместья, de la famille Buonaparte.
Non, je vous préviens, que si vous ne me dites pas, que nous avons la guerre, si vous vous permettez encore de pallier toutes
les infamies, toutes les atrocités de cet Antichrist (ma parole, j’y crois) — je ne vous connais plus, vous n’êtes plus mon ami,
vous n’êtes plus мой верный раб, comme vous dites.
Ну, здравствуйте, здравствуйте. Je vois que je vous fais peur, садитесь и рассказывайте.
Так говорила в июле 1805 года известная Анна Павловна Шерер, фрейлина и приближенная императрицы Марии Феодоровны, встречая важного
и чиновного князя Василия, первого приехавшего на ее вечер. Анна Павловна кашляла несколько дней, у нее был грипп, как она говорила
(грипп был тогда новое слово, употреблявшееся только редкими).
"""

@pytest.mark.version('>=5.0')
def test_1(act: Action, tmp_user: User, capsys):

    bpb_stream = bytes([1, BPBItem.TYPE, 1, BlobType.STREAM])

    def open_blob(cur: Cursor, blob_id, addi_msg = ''):
        tmp_blob = None
        print(addi_msg)
        try:
            tmp_blob = cur.connection._att.open_blob(cur.transaction._tra, blob_id, bpb_stream)
            blob_length = tmp_blob.get_info2(BlobInfoCode.TOTAL_LENGTH)
            segment_size = tmp_blob.get_info2(BlobInfoCode.MAX_SEGMENT)
            print(f'Blob opened OK, {hex(blob_id.low)=}; {hex(blob_id.high)=}, {blob_length=}, {segment_size=}')
        except DatabaseError as e:
            print( e.__str__() )
            print(e.gds_codes)
        finally:
            if tmp_blob is not None:
                tmp_blob.close()
                del tmp_blob

    v_blob_data_id = None
    with act.db.connect() as con_dba, act.db.connect(user=tmp_user.name, password=tmp_user.password) as con_usr:
        with con_dba.cursor() as cur_dba, con_usr.cursor() as cur_usr:
            id = None
            cur_dba.execute("create table blob_storage (b_field blob sub_type 1 segment size 4096)")
            con_dba.commit()
            cur_dba.execute(f"insert into blob_storage(b_field) values(?)", (BLOB_DATA,))
            con_dba.commit()
            cur_dba.execute(f"grant select on blob_storage to {tmp_user.name}")
            con_dba.commit()
            cur_dba.stream_blobs.append('b_field'.upper())
            cur_dba.execute("select b_field from blob_storage")

            v_blob_data_id = cur_dba.fetchone()[0].blob_id
            assert v_blob_data_id

            cur_usr._transaction.begin()

            open_blob(cur_usr, v_blob_data_id, 'Check #1.')

            cur_dba.execute(f"revoke select on blob_storage from {tmp_user.name}")
            con_dba.commit()

    assert v_blob_data_id

    with act.db.connect(user=tmp_user.name, password=tmp_user.password) as con_usr:
        with con_usr.cursor() as cur_usr:
            # Should fail
            cur_usr._transaction.begin()
            open_blob(cur_usr, v_blob_data_id, 'Check #2.')

    expected_stdout = f"""
        Check #1.
        Blob opened OK, hex(blob_id.low)='0x...'; hex(blob_id.high)='0x...', blob_length=N, segment_size=M

        Check #2.
        no permission for SELECT access to TABLE "PUBLIC"."BLOB_STORAGE"
        -Effective user is TMP_BLOB_READER
        (335544352, 335545254)
    """
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
