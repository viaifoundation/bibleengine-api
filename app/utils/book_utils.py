"""Bible book name utilities and lookup functions."""

# Book name arrays
BOOK_SHORT = [
    "", "Gen", "Exod", "Lev", "Num", "Deut", "Josh", "Judg", "Ruth", "1Sam",
    "2Sam", "1Kgs", "2Kgs", "1Chr", "2Chr", "Ezra", "Neh", "Esth", "Job",
    "Ps", "Prov", "Eccl", "Song", "Isa", "Jer", "Lam", "Ezek", "Dan", "Hos",
    "Joel", "Amos", "Obad", "Jonah", "Mic", "Nah", "Hab", "Zeph", "Hag",
    "Zech", "Mal", "Matt", "Mark", "Luke", "John", "Acts", "Rom", "1Cor",
    "2Cor", "Gal", "Eph", "Phil", "Col", "1Thess", "2Thess", "1Tim", "2Tim",
    "Titus", "Phlm", "Heb", "Jas", "1Pet", "2Pet", "1John", "2John", "3John",
    "Jude", "Rev"
]

BOOK_ENGLISH = [
    "", "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua",
    "Judges", "Ruth", "1 Samuel", "2 Samuel", "1 Kings", "2 Kings",
    "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah", "Esther", "Job",
    "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah",
    "Jeremiah", "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos",
    "Obadiah", "Jonah", "Micah", "Nahum", "Habakkuk", "Zephaniah", "Haggai",
    "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians",
    "Philippians", "Colossians", "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"
]

BOOK_CHINESE = [
    "", "创世记", "出埃及记", "利未记", "民数记", "申命记", "约书亚记",
    "士师记", "路得记", "撒母耳记上", "撒母耳记下", "列王纪上", "列王纪下",
    "历代志上", "历代志下", "以斯拉记", "尼希米记", "以斯帖记", "约伯记",
    "诗篇", "箴言", "传道书", "雅歌", "以赛亚书", "耶利米书", "耶利米哀歌",
    "以西结书", "但以理书", "何西阿书", "约珥书", "阿摩司书", "俄巴底亚书",
    "约拿书", "弥迦书", "那鸿书", "哈巴谷书", "西番雅书", "哈该书",
    "撒迦利亚书", "玛拉基书", "马太福音", "马可福音", "路加福音", "约翰福音",
    "使徒行传", "罗马书", "哥林多前书", "哥林多后书", "加拉太书", "以弗所书",
    "腓立比书", "歌罗西书", "帖撒罗尼迦前书", "帖撒罗尼迦后书", "提摩太前书",
    "提摩太后书", "提多书", "腓利门书", "希伯来书", "雅各书", "彼得前书",
    "彼得后书", "约翰一书", "约翰二书", "约翰三书", "犹大书", "启示录"
]

BOOK_COUNT = [
    0, 50, 40, 27, 36, 34, 24, 21, 4, 31, 24, 22, 25, 29, 36, 10, 13, 10, 42,
    150, 31, 12, 8, 66, 52, 5, 48, 12, 14, 3, 9, 1, 4, 7, 3, 3, 3, 2, 14, 4,
    28, 16, 24, 21, 28, 16, 16, 13, 6, 6, 4, 4, 5, 3, 6, 4, 3, 1, 13, 5, 5,
    3, 5, 1, 1, 1, 22
]

# Comprehensive book index for lookup (includes all variations)
BOOK_INDEX = {
    "1Ch": 13, "1 Chr": 13, "1Chr": 13, "1Chronicles": 13, "1 Chronicles": 13,
    "1Co": 46, "1 Cor": 46, "1Cor": 46, "1Corinthians": 46, "1 Corinthians": 46,
    "1J": 62, "1Jn": 62, "1Jo": 62, "1 John": 62, "1John": 62,
    "1K": 11, "1Kgs": 11, "1Ki": 11, "1 Kin": 11, "1Kings": 11, "1 Kings": 11,
    "1P": 60, "1Pe": 60, "1 Pet": 60, "1Pet": 60, "1Peter": 60, "1 Peter": 60,
    "1S": 9, "1Sa": 9, "1 Sam": 9, "1Sam": 9, "1Samuel": 9, "1 Samuel": 9,
    "1Th": 52, "1 Th": 52, "1 Thess": 52, "1Thess": 52, "1Thessalonians": 52, "1 Thessalonians": 52,
    "1Ti": 54, "1 Tim": 54, "1Tim": 54, "1Timothy": 54, "1 Timothy": 54, "1Tm": 54,
    "2Ch": 14, "2 Chr": 14, "2Chr": 14, "2Chronicles": 14, "2 Chronicles": 14,
    "2Co": 47, "2 Cor": 47, "2Cor": 47, "2Corinthians": 47, "2 Corinthians": 47,
    "2J": 63, "2Jn": 63, "2Jo": 63, "2 John": 63, "2John": 63,
    "2K": 12, "2Kgs": 12, "2Ki": 12, "2 Kin": 12, "2Kings": 12, "2 Kings": 12,
    "2P": 61, "2Pe": 61, "2 Pet": 61, "2Pet": 61, "2Peter": 61, "2 Peter": 61,
    "2S": 10, "2Sa": 10, "2 Sam": 10, "2Sam": 10, "2Samuel": 10, "2 Samuel": 10,
    "2Th": 53, "2 Th": 53, "2 Thess": 53, "2Thess": 53, "2Thessalonians": 53, "2 Thessalonians": 53,
    "2Ti": 55, "2 Tim": 55, "2Tim": 55, "2Timothy": 55, "2 Timothy": 55, "2Tm": 55,
    "3J": 64, "3Jn": 64, "3Jo": 64, "3 John": 64, "3John": 64,
    "Ac": 44, "Act": 44, "Acts": 44,
    "Am": 30, "Amo": 30, "Amos": 30,
    "Cs": 51, "Col": 51, "Colossians": 51,
    "Da": 27, "Dan": 27, "Daniel": 27,
    "De": 5, "Deu": 5, "Deut": 5, "Deuteronomy": 5,
    "Dn": 27, "Dt": 5,
    "Ec": 21, "Ecc": 21, "Eccl": 21, "Ecclesiastes": 21,
    "Ep": 49, "Eph": 49, "Ephesians": 49,
    "Es": 17, "Est": 17, "Esth": 17, "Esther": 17,
    "Ex": 2, "Exo": 2, "Exod": 2, "Exodus": 2,
    "Eze": 26, "Ezek": 26, "Ezekiel": 26,
    "Ezr": 15, "Ezra": 15,
    "Ga": 48, "Gal": 48, "Galatians": 48,
    "Ge": 1, "Gen": 1, "Genesis": 1, "Gn": 1,
    "Hab": 35, "Habakkuk": 35,
    "Hag": 37, "Haggai": 37,
    "Hb": 58, "Heb": 58, "Hebrews": 58,
    "Hg": 37, "Ho": 28, "Hos": 28, "Hosea": 28, "Hs": 28,
    "Is": 23, "Isa": 23, "Isaiah": 23,
    "Jam": 59, "James": 59, "Jas": 59,
    "Jb": 18, "Jd": 65, "Jdg": 7, "Jer": 24, "Jeremiah": 24,
    "Jg": 7, "Jl": 29, "Jm": 59, "Jn": 43, "Jnh": 32,
    "Job": 18, "Joe": 29, "Joel": 29, "Joh": 43, "John": 43,
    "Jon": 32, "Jonah": 32, "Jos": 6, "Josh": 6, "Joshua": 6,
    "Jr": 24, "Jud": 65, "Jude": 65, "Judg": 7, "Judges": 7,
    "La": 25, "Lam": 25, "Lamentations": 25,
    "Le": 3, "Lev": 3, "Leviticus": 3,
    "Lk": 42, "Lm": 25, "Lu": 42, "Luk": 42, "Luke": 42,
    "Lv": 3, "Mal": 39, "Malachi": 39,
    "Mar": 41, "Mark": 41, "Mat": 40, "Matt": 40, "Matthew": 40,
    "Mi": 33, "Mic": 33, "Micah": 33,
    "Mk": 41, "Mr": 41, "Mt": 40,
    "Na": 34, "Nah": 34, "Nahum": 34,
    "Ne": 16, "Neh": 16, "Nehemiah": 16,
    "Nm": 4, "No": 4, "Nu": 4, "Num": 4, "Numbers": 4,
    "Ob": 31, "Oba": 31, "Obad": 31, "Obadiah": 31,
    "Phi": 50, "Phil": 50, "Philem": 57, "Philemon": 57, "Philippians": 50,
    "Phlm": 57, "Phm": 57, "Php": 50, "Pm": 57, "Pp": 50,
    "Pr": 20, "Pro": 20, "Prov": 20, "Proverbs": 20,
    "Ps": 19, "Psa": 19, "Psalm": 19, "Psalms": 19,
    "Re": 66, "Rev": 66, "Revelation": 66,
    "Ro": 45, "Rom": 45, "Romans": 45, "Rm": 45,
    "Rt": 8, "Ru": 8, "Rut": 8, "Ruth": 8,
    "Rv": 66, "Sg": 22, "So": 22, "Son": 22, "Song": 22,
    "Song of Solomon": 22, "Song of Songs": 22, "SS": 22,
    "Tit": 56, "Titus": 56, "Tt": 56,
    "Zc": 38, "Zec": 38, "Zech": 38, "Zechariah": 38,
    "Zep": 36, "Zeph": 36, "Zephaniah": 36, "Zp": 36,
    # Chinese book names
    "书": 6, "亚": 38, "亞": 38, "代上": 13, "代下": 14,
    "以弗所书": 49, "以弗所書": 49, "以斯帖記": 17, "以斯帖记": 17,
    "以斯拉記": 15, "以斯拉记": 15, "以西結書": 26, "以西结书": 26,
    "以賽亞書": 23, "以赛亚书": 23, "传": 21, "传道书": 21,
    "伯": 18, "但": 27, "但以理书": 27, "但以理書": 27,
    "何": 28, "何西阿书": 28, "何西阿書": 28,
    "使徒行传": 44, "使徒行傳": 44, "來": 58, "俄": 31,
    "俄巴底亚书": 31, "俄巴底亞書": 31, "傳": 21, "傳道書": 21,
    "出": 2, "出埃及記": 2, "出埃及记": 2, "列王紀上": 11,
    "列王紀下": 12, "列王纪上": 11, "列王纪下": 12, "创": 1,
    "创世记": 1, "利": 3, "利未記": 3, "利未记": 3, "創": 1,
    "創世記": 1, "加": 48, "加拉太书": 48, "加拉太書": 48,
    "历代志上": 13, "历代志下": 14, "可": 41, "启": 66,
    "启示录": 66, "哀": 25, "哈": 35, "哈巴谷书": 35,
    "哈巴谷書": 35, "哈該書": 37, "哈该书": 37,
    "哥林多前书": 46, "哥林多前書": 46, "哥林多后书": 47,
    "哥林多後書": 47, "啟": 66, "啟示錄": 66, "士": 7,
    "士师记": 7, "士師記": 7, "多": 56, "太": 40, "尼": 16,
    "尼希米記": 16, "尼希米记": 16, "希伯來書": 58, "希伯来书": 58,
    "帖前": 52, "帖后": 53, "帖後": 53, "帖撒罗尼迦": 52,
    "帖撒羅尼迦": 53, "弗": 49, "弥": 33, "弥迦书": 33,
    "彌": 33, "彌迦書": 33, "彼前": 60, "彼后": 61, "彼後": 61,
    "彼得前书": 60, "彼得前書": 60, "彼得后书": 61, "彼得後書": 61,
    "徒": 44, "得": 8, "拉": 15, "拿": 32, "提前": 54,
    "提后": 55, "提多书": 56, "提多書": 56, "提後": 55,
    "提摩太前书": 54, "提摩太前書": 54, "提摩太后书": 55,
    "提摩太後書": 55, "摩": 30, "撒上": 9, "撒下": 10,
    "撒母耳記上": 9, "撒母耳記下": 10, "撒母耳记上": 9,
    "撒母耳记下": 10, "撒迦利亚书": 38, "撒迦利亞書": 38,
    "斯": 17, "書": 6, "来": 58, "林前": 46, "林后": 47,
    "林後": 47, "歌": 22, "歌罗西书": 51, "歌羅西書": 51,
    "约书亚记": 6, "约二": 63, "约贰": 63, "约伯记": 18,
    "约拿书": 32, "约珥书": 29, "约翰一书": 62, "约翰壹书": 62,
    "约翰三书": 64, "约翰叁书": 64, "约翰二书": 63, "约翰贰书": 63,
    "约翰福音": 43, "结": 26, "罗": 45, "罗马书": 45, "羅": 45,
    "羅馬書": 45, "耶": 24, "耶利米书": 24, "耶利米哀歌": 25,
    "耶利米書": 24, "腓": 50, "腓利門書": 57, "腓利门书": 57,
    "腓立比书": 50, "腓立比書": 50, "西": 51, "西番雅书": 36,
    "西番雅書": 36, "詩": 19, "詩篇": 19, "該": 37, "诗": 19,
    "诗篇": 19, "该": 37, "賽": 23, "赛": 23, "路": 42,
    "路加福音": 42, "路得記": 8, "路得记": 8, "那鴻書": 34,
    "那鸿书": 34, "門": 57, "门": 57, "阿摩司书": 30,
    "阿摩司書": 30, "雅": 59, "雅各书": 59, "雅各書": 59,
    "雅歌": 22, "馬可福音": 41, "馬太福音": 40, "马可福音": 41,
    "马太福音": 40, "鴻": 34, "鸿": 34
}


def get_book_id(book_name: str) -> int:
    """Get book ID from book name (supports multiple formats).
    
    Args:
        book_name: Book name in any format
        
    Returns:
        Book ID (1-66), 0 if not found
    """
    book_name = book_name.strip()
    return BOOK_INDEX.get(book_name, 0)


def get_book_short(book_id: int) -> str:
    """Get book short name by ID.
    
    Args:
        book_id: Book ID (1-66)
        
    Returns:
        Short name (e.g., "Gen", "创")
    """
    if 0 <= book_id < len(BOOK_SHORT):
        return BOOK_SHORT[book_id]
    return ""


def get_book_english(book_id: int) -> str:
    """Get book English name by ID.
    
    Args:
        book_id: Book ID (1-66)
        
    Returns:
        English name (e.g., "Genesis")
    """
    if 0 <= book_id < len(BOOK_ENGLISH):
        return BOOK_ENGLISH[book_id]
    return ""


def get_book_chapter_count(book_id: int) -> int:
    """Get book chapter count.
    
    Args:
        book_id: Book ID (1-66)
        
    Returns:
        Chapter count
    """
    if 0 <= book_id < len(BOOK_COUNT):
        return BOOK_COUNT[book_id]
    return 0

