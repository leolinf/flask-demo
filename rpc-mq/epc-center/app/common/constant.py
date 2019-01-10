# -*- coding = utf-8 -*-


class Code:
    """错误码"""

    SUCCESS = 1200
    SUCCESS_NOT_DATA = 1230
    MISSPARAM = 1002
    DATAERROR = 1005
    ICREDITEMPTY = 1006
    TSEPIRE = 1201
    TIMEOUTERROR = 1202
    TIMEOUT_ERROR = 1202
    INTERERROR = 1203
    INTER_ERROR = 1203
    VERIFYDENIED = 2000
    OVER_TEST = 2001
    SEARCH_ERROR = 2002
    KEYWORD_ERROR = 2003
    OTHER_ERROR = 2004
    UPDATE_ERROR = 2005
    SERVERS_ERROR = 2006
    PERMISSIONDENIED = 1301
    TIMEFORMATERROR = 1302
    TIMEFORMAT_ERROR = 1302
    INVALID_TEL = 1303
    MISSSIGN = 1304
    MISSAPPKEY = 1305
    IPERROR = 1306
    ERRORTIMESTAMP = 1307
    ERRORGET = 1308
    PERMISSIONTEST = 1309
    SUCCESS_RECORED = 1
    FAIL_PECORED = 0
    SIGN_FAILUER = 1310
    PARAM_ERROR = 1311
    FILE_IS_BIG = 1400
    UNQUALIFIED_PHOTO = 1402
    DECRYPT_FAILD = 1403


class Params:
    """必须的参数"""

    SIGN = "sign"
    TIMESTAMP = "t"
    APPKEY = "app_key"


class BrandFirstThreeLetter:
    """vin前三位对应品牌"""

    TOYOTA = ["NMT", "PA2", "PN2", "5TD", "4T1", "LFM", "RL4", "TW1", "JDA", "9BR", "JT1", "JT3", "MMK", "JHH", "9FH", "MR0", "JTE", "JTH", "7A4", "5YF", "4T2", "8AJ", "LFP", "MX1", "JTN", "MR1", "JTL", "JT2", "MHF", "PN1", "JTJ", "JT8", "JTF", "CA0", "6T1", "TW0", "JT4", "RUT", "LCU", "SB1", "AHT", "JF1", "6FH", "JTG", "JHG", "AHK", "8XA", "JT7", "RKL", "MHK", "JHD", "LVG", "JTM", "JTK", "JD6", "JHF", "JTC", "PA1", "JT6", "MR2", "JTB", "JTA", "8XB", "JTD", "4T3", "JYF", "LTV", "MBJ"]

    NISSAN = ["1N4", "1N6", "3N1", "3N6", "3N8", "3T3", "3TA", "4TA", "5N1", "5N3", "5TA", "65B", "94D", "ADN", "DA1", "DA6", "JN1", "JN6", "JN8", "JNK", "JNN", "JNR", "KNM", "LGB", "LJN", "MDH", "MNT", "MT8", "NME", "NTB", "RF5", "RLF", "RN3", "SJK", "SJN", "VNV", "VSK", "VWA", "Z8N"]
