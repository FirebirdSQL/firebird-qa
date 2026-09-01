#coding:utf-8

"""
ID:          n/a
ISSUE:       n/a
TITLE:       DECLARED TEMPORARY TABLE. Index usage when textual data belongs to Unicode ranges
DESCRIPTION:
    Test verifies ability to create DTT with indexed column which length equals to limit
    determined by the database page size and number of bytes per character.
    Ascending and descending indices are checked.
    Data that has been just inserted in the DTT is queried so that index must be used.
    Test query (which uses appropriate index) must return string that has been just inserted.
    
NOTES:
    Actual max length of index key depends NOT ONLY on page size but also on number of bytes per character.
    Explained by Adriano 26.06.2025 14:23, see subj "Index max length: weird limit (999 characters) ..."
    formula: (USHORT) (log10(inLen + 1.0) + 2) * 4 * impl->texttype_bytes_per_key ; see also src/intl/lc_narrow.cpp
    Because of that, testing character set is UTF8 but WITHOUT 'collate unicode_ci_ai' clause.
    Otherwise we may fall in runtime error depending on UNICODE_RANGE value.
    For example, attempt to insert following string generated in 'Katakana Phonetic Extensions':
    ㈸㊿㊝㈌㋅㉬㉂㉿㋁㈥㉕㈂㋥㋦㋏㈓㋉㊓㈀㈌㋶㈒㊪㉙㈴㈵㊯㊸㈞㋥㈦㋯㋨㉦㉏㉮㉿㋋㉍㊡㈐㊞㋠㊈㊛㊨㈪㊸㋏㊄㉀㉂㋨㈿㈓㊃㉨㊅㋤㈭㋨㊿㈻㈲㈳㈲㉘㉦㈗㈪㋐㈀㉶㉥㋫㊰㉵㈜㉵㉬㋑㋭㉉㉊㊃㋞㈩㊓㊛㉱㋱㋇㉎㊦㉬㉽㊇㈜㋋㉢㈛㊿㋝㊢㈤㊽㉔㋱㊖㋯㈐㊇㋡㉍㉓㋆㉉㈡㈌㋢㊨㋞㋥㋯㊷㈰㋇㋍㊁㈯㋻㈠㉪㈣㊴㉘㈝㈕㉽㈇㈲㊗㋊㊻㉭㊃㈷㉸㉇㊾㋂㊢㈐㈝㋮㉮㈰㊇㈉㉟㊜㈈㊌㋼㈊㊾㋋㋬㋙㈟㉭㉙㈀㉝㈪㈬㋽㈨㈕㊱㉏㉨㋑㈑㈅㉧㈅㊷㉈㈉㉤㋝㉟㋻㋐㈜㉌㈄㈸㊰㋬㊲㊤㋥㉇㉞㉁㉢㈴㉵㋇㋗㊏㈿㊨㋾㉍㋱㊖㉿㊙㉫㋝㋶㉵㋥㊧㊪㊸㉓㋍㊚㋓㉶㈭㈛㉜㈞㈇㈳㋰㊈㋯㈷㈙㊆㊢㉖㋊㉟㋜㉽㊔㈺㈑㉦㊤㉘㉧㉀㈎㈵㊷㋋㊺㈼㊐㊣㉊㉭㋕㊢㋻㊱㈛㈔㈯㉬㉫㊣㊆㋯㉶㊳㊶㋳㈇㈻㊺㉄㈚㈢㉓㈤㉬㉀㋔㉩㊢㈵㉁㈹㊇㉎㈛㋎㊌㋻㊘㊯㋷㊼
    causes:
    "SQLSTATE = 54000 / Error during savepoint backout - transaction invalidated / -Implementation limit ... / key size exceeds ..."

    Original commit:
        https://github.com/FirebirdSQL/firebird/commit/f93b6ce7ba148e6185c40a3328ca56686626e2ae

    [01.09.2026] pzotov
    Checked on 20260829_024127-6.0.0.2164-2d371e2.
"""
import time
import random
import locale
import pytest
from firebird.qa import *

PAGE_SIZE = 16384

# https://firebirdsql.org/file/documentation/html/en/refdocs/fblangref50/firebird-50-language-reference.html#fblangref50-datatypes-chartypes-charindxs
NAME_MAX_LEN = int((PAGE_SIZE/4-9)//6)
NAME_MIN_LEN = NAME_MAX_LEN

# how many random rows to generate for each unicode range:
ROWS_PER_ONE_UNICODE_RANGE = 30

init_script = f"""
    create domain dm_text varchar({NAME_MAX_LEN}) character set utf8;
    create domain dm_unicode_range varchar(80);
    create table test_rnd_unicode(unicode_random_txt dm_text unique using index txt_unq, unicode_range_name dm_unicode_range);
"""
db = db_factory(init = init_script, charset = 'utf8', page_size = PAGE_SIZE)

substitutions = [('[ \t]+', ' '), (r'line: \d+, col: \d+', '')]
act = python_act('db', substitutions = substitutions)

#------------------------------------------------

def get_random_unicode(length, bound_points):
    # https://stackoverflow.com/questions/1477294/generate-random-utf-8-string-in-python
    try:
        get_char = unichr
    except NameError:
        get_char = chr

    alphabet = [
        get_char(code_point) for code_point in range(bound_points[0],bound_points[1])
    ]
    return ''.join(random.choice(alphabet) for i in range(length))

#------------------------------------------------

@pytest.mark.version('>=6.0')
def test_1(act: Action, capsys):

    # https://jrgraphix.net/r/Unicode/
    UNICODE_RANGES_MAP = {
        (0x0020, 0x007F) : 'Basic Latin',
        (0x00A0, 0x00FF) : 'Latin-1 Supplement',
        (0x0100, 0x017F) : 'Latin Extended-A',
        (0x0180, 0x024F) : 'Latin Extended-B',
        (0x0400, 0x04FF) : 'Cyrillic',
        (0x0500, 0x052F) : 'Cyrillic Supplementary',
        (0x0300, 0x036F) : 'Combining Diacritical Marks',
        (0x0250, 0x02AF) : 'IPA Extensions',
        (0x0370, 0x03FF) : 'Greek and Coptic',
        (0x0530, 0x058F) : 'Armenian',
        (0x02B0, 0x02FF) : 'Spacing Modifier Letters',
        (0x0590, 0x05FF) : 'Hebrew',
        (0x0600, 0x06FF) : 'Arabic',
        (0x0700, 0x074F) : 'Syriac',
        (0x0780, 0x07BF) : 'Thaana',
        (0x0900, 0x097F) : 'Devanagari',
        (0x0980, 0x09FF) : 'Bengali',
        (0x0A00, 0x0A7F) : 'Gurmukhi',
        (0x0A80, 0x0AFF) : 'Gujarati',
        (0x0B00, 0x0B7F) : 'Oriya',
        (0x0B80, 0x0BFF) : 'Tamil',
        (0x0C00, 0x0C7F) : 'Telugu',
        (0x0C80, 0x0CFF) : 'Kannada',
        (0x0D00, 0x0D7F) : 'Malayalam',
        (0x0D80, 0x0DFF) : 'Sinhala',
        (0x0E00, 0x0E7F) : 'Thai',
        (0x0E80, 0x0EFF) : 'Lao',
        (0x0F00, 0x0FFF) : 'Tibetan',
        (0x1000, 0x109F) : 'Myanmar',
        (0x10A0, 0x10FF) : 'Georgian',
        (0x1100, 0x11FF) : 'Hangul Jamo',
        (0x1200, 0x137F) : 'Ethiopic',
        (0x13A0, 0x13FF) : 'Cherokee',
        (0x1400, 0x167F) : 'Unified Canadian Aboriginal Syllabics',
        (0x1680, 0x169F) : 'Ogham',
        (0x16A0, 0x16FF) : 'Runic',
        (0x1700, 0x171F) : 'Tagalog',
        (0x1720, 0x173F) : 'Hanunoo',
        (0x1740, 0x175F) : 'Buhid',
        (0x1760, 0x177F) : 'Tagbanwa',
        (0x1780, 0x17FF) : 'Khmer',
        (0x1800, 0x18AF) : 'Mongolian',
        (0x1900, 0x194F) : 'Limbu',
        (0x1950, 0x197F) : 'Tai Le',
        (0x19E0, 0x19FF) : 'Khmer Symbols',
        (0x1D00, 0x1D7F) : 'Phonetic Extensions',
        (0x1E00, 0x1EFF) : 'Latin Extended Additional',
        (0x1F00, 0x1FFF) : 'Greek Extended',
        (0x2000, 0x206F) : 'General Punctuation',
        (0x2070, 0x209F) : 'Superscripts and Subscripts',
        (0x20A0, 0x20CF) : 'Currency Symbols',
        (0x20D0, 0x20FF) : 'Combining Diacritical Marks for Symbols',
        (0x2100, 0x214F) : 'Letterlike Symbols',
        (0x2150, 0x218F) : 'Number Forms',
        (0x2190, 0x21FF) : 'Arrows',
        (0x2200, 0x22FF) : 'Mathematical Operators',
        (0x2300, 0x23FF) : 'Miscellaneous Technical',
        (0x2400, 0x243F) : 'Control Pictures',
        (0x2440, 0x245F) : 'Optical Character Recognition',
        (0x2460, 0x24FF) : 'Enclosed Alphanumerics',
        (0x2500, 0x257F) : 'Box Drawing',
        (0x2580, 0x259F) : 'Block Elements',
        (0x25A0, 0x25FF) : 'Geometric Shapes',
        (0x2600, 0x26FF) : 'Miscellaneous Symbols',
        (0x2700, 0x27BF) : 'Dingbats',
        (0x27C0, 0x27EF) : 'Miscellaneous Mathematical Symbols-A',
        (0x27F0, 0x27FF) : 'Supplemental Arrows-A',
        (0x2800, 0x28FF) : 'Braille Patterns',
        (0x2900, 0x297F) : 'Supplemental Arrows-B',
        (0x2980, 0x29FF) : 'Miscellaneous Mathematical Symbols-B',
        (0x2A00, 0x2AFF) : 'Supplemental Mathematical Operators',
        (0x2B00, 0x2BFF) : 'Miscellaneous Symbols and Arrows',
        (0x2E80, 0x2EFF) : 'CJK Radicals Supplement',
        (0x2F00, 0x2FDF) : 'Kangxi Radicals',
        (0x2FF0, 0x2FFF) : 'Ideographic Description Characters',
        (0x3000, 0x303F) : 'CJK Symbols and Punctuation',
        (0x3040, 0x309F) : 'Hiragana',
        (0x30A0, 0x30FF) : 'Katakana',
        (0x3100, 0x312F) : 'Bopomofo',
        (0x3130, 0x318F) : 'Hangul Compatibility Jamo',
        (0x3190, 0x319F) : 'Kanbun',
        (0x31A0, 0x31BF) : 'Bopomofo Extended',
        (0x31F0, 0x31FF) : 'Katakana Phonetic Extensions',
        (0x3200, 0x32FF) : 'Enclosed CJK Letters and Months',
        (0x3300, 0x33FF) : 'CJK Compatibility',
        (0x3400, 0x4DBF) : 'CJK Unified Ideographs Extension A',
        (0x4DC0, 0x4DFF) : 'Yijing Hexagram Symbols',
        (0x4E00, 0x9FFF) : 'CJK Unified Ideographs',
        (0xA000, 0xA48F) : 'Yi Syllables',
        (0xA490, 0xA4CF) : 'Yi Radicals',
        (0xAC00, 0xD7AF) : 'Hangul Syllables',
        (0xE000, 0xF8FF) : 'Private Use Area',
        (0xF900, 0xFAFF) : 'CJK Compatibility Ideographs',
        (0xFB00, 0xFB4F) : 'Alphabetic Presentation Forms',
        (0xFB50, 0xFDFF) : 'Arabic Presentation Forms-A',
        (0xFE00, 0xFE0F) : 'Variation Selectors',
        (0xFE20, 0xFE2F) : 'Combining Half Marks',
        (0xFE30, 0xFE4F) : 'CJK Compatibility Forms',
        (0xFE50, 0xFE6F) : 'Small Form Variants',
        (0xFE70, 0xFEFF) : 'Arabic Presentation Forms-B',
        (0xFF00, 0xFFEF) : 'Halfwidth and Fullwidth Forms',
        (0xFFF0, 0xFFFF) : 'Specials',
        (0x10000, 0x1007F) : 'Linear B Syllabary',
        (0x10080, 0x100FF) : 'Linear B Ideograms',
        (0x10100, 0x1013F) : 'Aegean Numbers',
        (0x10300, 0x1032F) : 'Old Italic',
        (0x10330, 0x1034F) : 'Gothic',
        (0x10380, 0x1039F) : 'Ugaritic',
        (0x10400, 0x1044F) : 'Deseret',
        (0x10450, 0x1047F) : 'Shavian',
        (0x10480, 0x104AF) : 'Osmanya',
        (0x10800, 0x1083F) : 'Cypriot Syllabary',
        (0x1D000, 0x1D0FF) : 'Byzantine Musical Symbols',
        (0x1D100, 0x1D1FF) : 'Musical Symbols',
        (0x1D300, 0x1D35F) : 'Tai Xuan Jing Symbols',
        (0x1D400, 0x1D7FF) : 'Mathematical Alphanumeric Symbols',
        (0x20000, 0x2A6DF) : 'CJK Unified Ideographs Extension B',
        (0x2F800, 0x2FA1F) : 'CJK Compatibility Ideographs Supplement',
        (0xE0000, 0xE007F) : 'Tags',
    }
    with act.db.connect(charset = 'utf8') as con:
        cur = con.cursor()
        ps = cur.prepare('update or insert into test_rnd_unicode(unicode_random_txt, unicode_range_name) values(?, ?) matching(unicode_random_txt)')
        for bound_points, range_name in UNICODE_RANGES_MAP.items():
            for i in range(ROWS_PER_ONE_UNICODE_RANGE):
                unicode_rnd_txt = get_random_unicode( random.randint(NAME_MIN_LEN, NAME_MAX_LEN), bound_points )
                cur.execute(ps, (unicode_rnd_txt, range_name) )

        con.commit()

    test_script = """
        set bail on;
        set autoterm on;
        set list on;
        commit;
        execute block returns(problematic_unicode_txt dm_text, unicode_range_name dm_unicode_range, index_dir varchar(3)) as
            declare temporary table ltt_unicode_asc(unicode_random_txt dm_text, unicode_range_name dm_unicode_range)
            ascending index ltt_unicode_asc(unicode_random_txt)
            ;
            declare temporary table ltt_unicode_dec(unicode_random_txt dm_text, unicode_range_name dm_unicode_range)
            descending index ltt_unicode_dec(unicode_random_txt)
            ;
            declare v_unicode_random_txt dm_text;
        begin
            for
                select unicode_random_txt, unicode_range_name from test_rnd_unicode
                as cursor c
            do begin
                rdb$set_context('USER_SESSION', 'DBG_RANDOM_TXT', c.unicode_random_txt);
                rdb$set_context('USER_SESSION', 'DBG_RANGE_NAME', c.unicode_range_name);

                insert into ltt_unicode_asc(unicode_random_txt, unicode_range_name) values(c.unicode_random_txt, c.unicode_range_name);
                insert into ltt_unicode_dec(unicode_random_txt, unicode_range_name) values(c.unicode_random_txt, c.unicode_range_name);

                v_unicode_random_txt = null;
                -- Following query uses index LTT_UNICODE_ASC Range Scan (lower bound: 1/1) and MUST return just inserted line:
                select min(u.unicode_random_txt) from ltt_unicode_asc u where u.unicode_random_txt >= c.unicode_random_txt into v_unicode_random_txt;
                if (v_unicode_random_txt is distinct from c.unicode_random_txt) then
                begin
                    problematic_unicode_txt = c.unicode_random_txt;
                    unicode_range_name = c.unicode_range_name;
                    index_dir = 'asc';
                    suspend;
                end

                v_unicode_random_txt = null;
                -- Following query will use index LTT_UNICODE_DEC Range Scan (lower bound: 1/1) and MUST return just inserted line:
                select max(u.unicode_random_txt) from ltt_unicode_dec u where u.unicode_random_txt <= c.unicode_random_txt into v_unicode_random_txt;
                if (v_unicode_random_txt is distinct from c.unicode_random_txt) then
                begin
                    problematic_unicode_txt = c.unicode_random_txt;
                    unicode_range_name = c.unicode_range_name;
                    index_dir = 'dec';
                    suspend;
                end

            end
        end
        ;
    """

    act.expected_stdout = f"""
    """
    act.isql(switches=['-q'], charset = 'utf8', input = test_script, combine_output = True, io_enc = 'utf-8')
    assert act.clean_stdout == act.clean_expected_stdout
    act.reset()
