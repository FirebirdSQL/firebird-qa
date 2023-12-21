#coding:utf-8

"""
ID:          issue-5770
ISSUE:       5770
TITLE:       Unclear gstat's diagnostic when damaged page in DB file appears encrypted
DESCRIPTION:
  Test creates table 'TEST' with varchar and blob fields, + index on varchar, and add some data to it.
  Blob field is filled by long values in order to prevent acomodation of its content within data pages.
  As result, this table should have pages of three different types: DataPage, BTreePage and BlobPage.

  Then we find number of first PP of this table by scrolling RDB$PAGES join RDB$RELATIONS result set.
  After this we:
  * define type of every page starting from first PP for 'TEST' table and up to total pages of DB,
    and doing this for each subsequent page, until ALL THREE different page types will be detected:
    1) data page, 2) index B-Tree and 3) blob page.
    These page numbers are stored in variables: (brk_datapage, brk_indxpage, brk_blobpage).
    When all three page numbers are found, loop is terminated;
  * close connection and open dB as binary file for reading and writing;
  * store previous content of .fdb in variable 'raw_db_content' (for further restore);
  * move file seek pointer at the beginning of every page from list: (brk_datapage, brk_indxpage, brk_blobpage);
  * BREAK page content by writing invalid binary data in the header of page;
    This invalid data are: bytes 0...7 ==> 0xFFAACCEEBB0000CC; bytes 8...15 ==> 0xDDEEAADDCC00DDEE;
  * Close DB file handle and:
  ** 1) run 'gstat -e';
  ** 2) run online validation;
  * open DB file again as binary and restore its content from var. 'raw_db_content' in order
    fbtest framework could finish this test (by making connect and drop this database);

  KEY POINTS:
  * report of 'gstat -e' should contain line with text 'ENCRYPTED 3 (DB problem!)'
    (number '3' should present becase we damaged pages of THREE diff. types: DP, BTree and Blob).
  * report of online validation should contain lines with info about three diff. page types which have problems.
JIRA:        CORE-5501
FBTEST:      bugs.core_5501
NOTES:
    [08.12.2021] pcisar
      Reimplementation does not work as expected on Linux FB 4.0 and 3.0.8
      gstat output:
        Data pages: total 97, encrypted 0, non-crypted 97
        Index pages: total 85, encrypted 0, non-crypted 85
        Blob pages: total 199, encrypted 0, non-crypted 199
        Generator pages: total 1, encrypted 0, non-crypted 1
      Validation does not report BLOB page errors, only data and index corruptions.

    [18.09.2022] pzotov
    Probably old-style bytesarreay was the reason of why pages were not considered by gstat as of unknown type.
    Decided to replace is with 'really random content, see 'os.urandom(<length>)'
    This is the only change, and after it was done test works fine.

    Checked on 3.0.8.33535 (SS/CS), 4.0.1.2692 (SS/CS), 5.0.0.730 (SS/CS) - both Linux and Windows.
"""
#from __future__ import annotations
import os
import time
from typing import Dict
import pytest
import re
from struct import unpack_from
from firebird.qa import *
from firebird.driver import Connection

init_script = """
    alter database drop linger;
    commit;

    create table test(s varchar(1000) unique using index test_s_unq, b blob);
    commit;

    set count on;
    insert into test(s, b)
    select
        rpad( '',1000, uuid_to_char(gen_uuid()) ),
        rpad( '',
              10000, -- NB: blob should have a big size! It should NOT be stored withih a data page.
              'qwertyuioplkjhgfdsazxcvbnm0987654321')
    from rdb$types
    rows 100;
    commit;
"""

db = db_factory(init=init_script)

substitutions=[
                ('total \\d+,', 'total'),
                ('non-crypted \\d+', 'non-crypted'),
                ('crypted \\d+', 'crypted'),
                ('Other pages.*', ''),
              ]

act = python_act('db', substitutions = substitutions)

expected_stdout = """
    Data pages: total 63, encrypted 0, non-crypted 63
    Index pages: total 88, encrypted 0, non-crypted 88
    Blob pages: total 199, encrypted 0, non-crypted 199
    Other pages: total 115, ENCRYPTED 3 (DB problem!), non-crypted 112
    Detected all THREE page types with problem => YES
"""

PAGE_TYPES = {0: "undef/free",
              1: "DB header",
              2: "PIP",
              3: "TIP",
              4: "Pntr Page",
              5: "Data Page",
              6: "Indx Root",
              7: "Indx Data",
              8: "Blob Page",
              9: "Gens Page",
              10: "SCN" # only for ODS>=12
             }

def fill_dbo(con: Connection, map_dbo: Dict):
    cur = con.cursor()
    sql = """
        select rel_id, rel_name, idx_id, idx_name
        from (
            select
                rr.rdb$relation_id rel_id,                  -- 0
                rr.rdb$relation_name rel_name,              -- 1
                -1 idx_id,                                  -- 2
                '' idx_name,                                -- 3
                rr.rdb$relation_type rel_type,
                rr.rdb$system_flag sys_flag
            from rdb$relations rr

            union all

            select
                rr.rdb$relation_id rel_id,                  -- 0
                rr.rdb$relation_name rel_name,              -- 1
                coalesce(ri.rdb$index_id-1,-1) idx_id,      -- 2
                coalesce(ri.rdb$index_name,'') idx_name,    -- 3
                rr.rdb$relation_type rel_type,
                rr.rdb$system_flag sys_flag
            from rdb$relations rr
            join rdb$indices ri on
            rr.rdb$relation_name = ri.rdb$relation_name
        ) r
        where
            coalesce(r.rel_type,0) = 0 --  exclude views, GTT and external tables
            and r.sys_flag is distinct from 1
"""
    cur.execute(sql)
    for r in cur:
        map_dbo[r[0], r[2]] = (r[1].strip(), r[3].strip())

def parse_page_header(con: Connection, page_number: int, map_dbo: Dict):
    page_buffer = con.info.get_page_content(page_number)

    # dimitr, 20.01.2017 ~13:00
    # all *CHAR = 1 byte, *SHORT = 2 bytes, *LONG = 4 bytes.

    # https://docs.python.org/2/library/struct.html
    # struct.unpack_from(fmt, buffer[, offset=0])
    # Unpack the buffer according to the given format.
    # The result is a tuple even if it contains exactly one item.
    # The buffer must contain at least the amount of data required by the format
    # len(buffer[offset:]) must be at least calcsize(fmt).
    # First character of the format string can be used to indicate the byte order,
    # size and alignment of the packed data
    # Native byte order is big-endian or little-endian:
    # <     little-endian
    # >     big-endian
    # Intel x86 and AMD64 (x86-64) are little-endian
    # Use sys.byteorder to check the endianness of your system:
    # https://docs.python.org/2/library/struct.html#format-characters
    # c     char     string of length 1
    # b     signed char
    # B     unsigned char
    # h     short
    # H     unsigned short     integer
    # i     int     integer 4
    # I     unsigned int     integer     4
    # l     long (4)
    # L     unsigned long (4)
    # q     long long (8)
    # Q     unsigned long long

    page_type = unpack_from('<b', page_buffer)[0]

    relation_id = -1
    index_id = -1
    segment_cnt = -1 # for Data page: number of record segments on page
    index_id = -1
    ix_level = -1
    btr_len = -1

    if page_type == 4:
        # POINTER pege:
        # *pag* dpg_header=16, SLONG dpg_sequence=4, SLONG ppg_next=4, USHORT ppg_count=2 ==> 16+4+4+2=26
        # struct pointer_page
        # {
        #     pag ppg_header;
        #     SLONG ppg_sequence;   // Sequence number in relation
        #     SLONG ppg_next;       // Next pointer page in relation
        #     USHORT ppg_count;     // Number of slots active
        #     USHORT ppg_relation;  // Relation id
        #     USHORT ppg_min_space; // Lowest slot with space available
        #     USHORT ppg_max_space; // Highest slot with space available
        #     SLONG ppg_page[1];    // Data page vector
        # };
        relation_id = unpack_from('<H', page_buffer, 26)[0] # 'H' ==> USHORT
    elif page_type == 5:
        # DATA page:
        # *pag* dpg_header=16, SLONG dpg_sequence=4 ==> 16+4 = 20:
        # struct data_page
        # {
        #   16  pag dpg_header;
        #    4 SLONG dpg_sequence;   // Sequence number in relation
        #    2 USHORT dpg_relation;  // Relation id
        #    2 USHORT dpg_count;     // Number of record segments on page
        #     struct dpg_repeat
        #     {
        #         USHORT dpg_offset; // Offset of record fragment
        #         USHORT dpg_length; // Length of record fragment
        #     } dpg_rpt[1];
        # };
        relation_id = unpack_from('<H', page_buffer, 20)[0] # 'H' ==> USHORT
        segment_cnt = unpack_from('<H', page_buffer, 22)[0]
    elif page_type == 6:
        # Index root page
        # struct index_root_page
        # {
        #     pag irt_header;
        #     USHORT irt_relation;            // relation id (for consistency)
        relation_id = unpack_from('<H', page_buffer, 16)[0] # 'H' ==> USHORT
    elif page_type == 7:
        # B-tree page ("bucket"):
        # struct btree_page
        # {
        # 16   pag btr_header;
        #  4   SLONG btr_sibling;         // right sibling page
        #  4   SLONG btr_left_sibling;    // left sibling page
        #  4   SLONG btr_prefix_total;    // sum of all prefixes on page
        #  2   USHORT btr_relation;       // relation id for consistency
        #  2   USHORT btr_length;         // length of data in bucket
        #  1   UCHAR btr_id;              // index id for consistency
        #  1   UCHAR btr_level;           // index level (0 = leaf)
        #     btree_nod btr_nodes[1];
        # };
        relation_id = unpack_from('<H', page_buffer, 28)[0]  # 'H' ==> USHORT
        btr_len = unpack_from('<H', page_buffer, 30)[0]  # 'H' ==> USHORT // length of data in bucket
        index_id = unpack_from('<B', page_buffer, 32)[0] # 'B' => UCHAR
        ix_level = unpack_from('<B', page_buffer, 33)[0]
    #
    if index_id>=0 and (relation_id, index_id) in map_dbo:
        u = map_dbo[ relation_id, index_id ]
        page_info = f'{PAGE_TYPES[page_type].ljust(9)}, {u[1].strip()}, data_len={btr_len}, lev={ix_level}'
        #page_info = ''.join((PAGE_TYPES[page_type].ljust(9), ', ', u[1].strip(), ', data_len=', str(btr_len), ', lev=', str(ix_level))) # 'Indx Page, <index_name>, <length of data in bucket>'
    elif (relation_id, -1) in map_dbo:
        u = map_dbo[ relation_id, -1 ]
        if page_type == 5:
            page_info = f'{PAGE_TYPES[page_type].ljust(9)}, {u[0].strip()}, segments on page: {segment_cnt}'
            #page_info = ''.join( ( PAGE_TYPES[page_type].ljust(9),', ',u[0].strip(),', segments on page: ',str(segment_cnt) ) ) # '<table_name>, segments on page: NNN' - for Data page
        else:
            page_info = f'{PAGE_TYPES[page_type].ljust(9)}, {u[0].strip()}'
            #page_info = ''.join( ( PAGE_TYPES[page_type].ljust(9),', ',u[0].strip() ) ) # '<table_name>' - for Pointer page
    elif relation_id == -1:
        page_info = PAGE_TYPES[page_type].ljust(9)
    else:
        page_info = f'UNKNOWN; {PAGE_TYPES[page_type].ljust(9)}; relation_id {relation_id}; index_id {index_id}'
        #page_info = ''.join( ('UNKNOWN; ',PAGE_TYPES[page_type].ljust(9),'; relation_id ', str(relation_id), '; index_id ', str(index_id)) )
    return (page_type, relation_id, page_info)

@pytest.mark.version('>=3.0.2')
def test_1(act: Action, capsys):
    map_dbo = {}
    sql = """
        select p.rdb$relation_id, p.rdb$page_number
        from rdb$pages p
        join rdb$relations r on p.rdb$relation_id = r.rdb$relation_id
        where r.rdb$relation_name=upper('TEST') and p.rdb$page_type = 4
        order by p.rdb$page_number
        rows 1
    """
    with act.db.connect() as con:
        fill_dbo(con, map_dbo)
        c = con.cursor()
        rel_id, pp1st = c.execute(sql).fetchone()
        # Found first page for each of three types: Data, Index and Blob
        # (loop starts from first PointerPage of table 'TEST')
        brk_datapage = brk_indxpage = brk_blobpage = -1
        for i in range(pp1st, con.info.pages_allocated):
            page_type, relation_id, page_info = parse_page_header(con, i, map_dbo)
            #print('page:',i, '; page_type:',page_type, '; rel_id:',relation_id,';',  page_info)
            if relation_id == 128 and page_type == 5:
                brk_datapage = i
            elif relation_id == 128 and page_type == 7:
                brk_indxpage = i
            elif page_type == 8:
                brk_blobpage = i
            if brk_datapage > 0 and brk_indxpage > 0 and brk_blobpage > 0:
                break

    # 3.0.8: 187; 184; 186
    #
    # Store binary content of .fdb for futher restore
    raw_db_content = act.db.db_path.read_bytes()

    # Make pages damaged: put random 16 bytes at the start of every page that we found:
    bw = bytearray(os.urandom(16))
    with open(act.db.db_path, 'r+b') as w:
        for brk_page in (brk_datapage, brk_indxpage, brk_blobpage):
            w.seek(brk_page * con.info.page_size)
            w.write(bw)
    
    #time.sleep(2) # ?!

    # Validate DB - ensure that there are errors in pages
    # RESULT: validation log should contain lines with problems about three diff. page types:
    # expected data encountered unknown
    # expected index B-tree encountered unknown
    # expected blob encountered unknown
    with act.connect_server() as srv:
        srv.database.validate(database=act.db.db_path, lock_timeout=1)
        validation_log = srv.readlines()

    # gstat
    act.gstat(switches=['-e'])

    pattern = re.compile('(data|index|blob|other)\\s+pages[:]{0,1}\\s+total[:]{0,1}\\s+\\d+[,]{0,1}\\s+encrypted[:]{0,1}\\s+\\d+.*[,]{0,1}non-crypted[:]{0,1}\\s+\\d+.*', re.IGNORECASE)
    for line in act.stdout.splitlines():
        if pattern.match(line.strip()):
            print(line.strip())

    # Process validation log
    data_page_problem = indx_page_problem = blob_page_problem = False
    for line in validation_log:
        if 'expected data' in line:
            data_page_problem = True
        elif 'expected index B-tree' in line:
            indx_page_problem = True
        elif 'expected blob' in line:
            blob_page_problem = True

    final_msg='Detected all THREE page types with problem => '
    if data_page_problem and indx_page_problem and blob_page_problem:
        final_msg += 'YES'
        print(final_msg)
    else:
        final_msg += 'NO'
        print(final_msg)
        print('Check output of "gstat -e":')
        for line in act.stdout.splitlines():
            print(line.replace(' ','.'))
        print('-' * 50)
        print(f'brk_datapage = {brk_datapage}, brk_indxpage = {brk_indxpage}, brk_blobpage = {brk_blobpage}')
        print(f'data_page_problem = {data_page_problem}, indx_page_problem = {indx_page_problem}, blob_page_problem = {blob_page_problem}')

    # restore DB content
    act.db.db_path.write_bytes(raw_db_content)

    act.reset()
    act.expected_stdout = expected_stdout
    act.stdout = capsys.readouterr().out
    assert act.clean_stdout == act.clean_expected_stdout
