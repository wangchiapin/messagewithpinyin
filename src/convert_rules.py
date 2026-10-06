"""把 GoodTeacher 的 rules.csv 轉成網頁引擎用的 JSON。

每條規則轉成 [字, 讀音, 前文序列, 後文序列]，讀音已經算好：
  - 「改」且有讀音提示 → 用提示
  - 「改」沒有提示 → 用下面 IDX 表（ToneOZ 讀音編號對應的讀音）
  - 「不改」 → 用 DEFAULT 表（ToneOZ 預設讀音）
GT_SIMP9、GT_SDEF 是字體內部的簡體預設字形處理，網頁用不到，略過。
"""
import csv, json, sys, unicodedata

SKIP_GROUPS = {'GT_SIMP9', 'GT_SDEF'}

# ToneOZ 預設讀音（「不改」或沒有規則符合時用）
DEFAULT = {
    '一': 'yī', '不': 'bù', '子': 'zǐ', '行': 'xíng', '重': 'zhòng',
    '長': 'cháng', '长': 'zhǎng', '了': 'le', '得': 'dé', '的': 'de',
    '著': 'zhe', '着': 'zháo', '覺': 'jué', '觉': 'jué', '樂': 'lè', '乐': 'lè',
    '更': 'gèng', '好': 'hǎo', '種': 'zhǒng', '种': 'zhǒng',
    '傳': 'chuán', '传': 'chuán', '會': 'huì', '会': 'kuài', '都': 'dōu',
    '數': 'shù', '数': 'shù', '背': 'bèi', '便': 'biàn', '量': 'liàng',
    '假': 'jiǎ', '調': 'tiáo', '调': 'diào', '教': 'jiào', '還': 'hái', '还': 'hái',
    '為': 'wéi', '为': 'wèi', '和': 'hé', '個': 'gè', '个': 'ge', '相': 'xiàng',
    '倒': 'dào', '應': 'yīng', '应': 'yīng', '省': 'shěng',
    '差': 'chā', '地': 'dì', '中': 'zhōng', '少': 'shǎo', '空': 'kōng',
    '朝': 'cháo', '處': 'chǔ', '处': 'chù', '給': 'gěi', '给': 'gěi',
    '落': 'luò', '供': 'gōng', '興': 'xīng', '兴': 'xīng',
    '參': 'cān', '参': 'cān', '沒': 'méi', '没': 'méi', '說': 'shuō', '说': 'shuō',
    '吐': 'tǔ', '发': 'fā', '切': 'qiē',
    # 親屬稱謂（編號 1 = 輕聲）
    '媽': 'mā', '妈': 'mā', '爸': 'bà', '爺': 'yé', '爷': 'yé', '奶': 'nǎi',
    '哥': 'gē', '姐': 'jiě', '姊': 'jiě', '弟': 'dì', '妹': 'mèi', '叔': 'shū',
    '舅': 'jiù', '姑': 'gū', '婆': 'pó', '公': 'gōng', '娃': 'wá', '寶': 'bǎo',
    '宝': 'bǎo', '嫂': 'sǎo', '爹': 'diē', '娘': 'niáng', '嬸': 'shěn', '婶': 'shěn', '伯': 'bó',
}

def neutral(s):
    return unicodedata.normalize('NFC', ''.join(
        c for c in unicodedata.normalize('NFD', s) if c not in '̀́̄̌'))

# ToneOZ 讀音編號 → 讀音（只列 CSV 裡「改」但沒寫提示的情況）
IDX = {
    ('长', '1'): 'cháng', ('着', '4'): 'zhe', ('种', '1'): 'zhǒng', ('会', '2'): 'huì',
    ('调', '1'): 'tiáo', ('还', '2'): 'hái', ('为', '1'): 'wéi', ('个', '1'): 'gè',
    ('倒', '1'): 'dǎo', ('應', '1'): 'yìng', ('应', '1'): 'yìng', ('省', '1'): 'xǐng',
    ('处', '1'): 'chǔ', ('參', '1'): 'shēn', ('參', '2'): 'cēn',
    ('参', '1'): 'cān', ('参', '2'): 'shēn', ('参', '3'): 'cēn',
    ('沒', '1'): 'mò', ('没', '1'): 'mò', ('說', '1'): 'shuì', ('说', '1'): 'shuì',
    ('吐', '1'): 'tù', ('发', '2'): 'fà',
}
KIN = '媽妈爸爺爷奶哥姐姊弟妹叔舅姑婆公娃寶宝嫂爹娘嬸婶伯'
for c in KIN:
    IDX[(c, '1')] = neutral(DEFAULT[c])


def seq(field):
    """'星|期' → ['星', '期']；'@GT_HANZI' 保留成代號。"""
    return [p for p in field.split('|')] if field else []


def main(src, dst):
    rows = list(csv.DictReader(open(src, encoding='utf-8-sig')))
    out, problems = [], []
    for n, r in enumerate(rows, start=2):
        if r['群組'] in SKIP_GROUPS:
            continue
        ch = r['字']
        if r['動作'] == '不改':
            py = DEFAULT.get(ch)
        else:
            py = r['讀音提示'].strip() or IDX.get((ch, r['讀音編號']))
        if not py:
            problems.append(f'第 {n} 行：{ch} 編號 {r["讀音編號"]} 找不到讀音')
            continue
        out.append([ch, py, seq(r['前文']), seq(r['後文'])])
    json.dump({'rules': out, 'defaults': DEFAULT}, open(dst, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print(f'{len(out)} 條規則寫入 {dst}')
    for p in problems:
        print('!!', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2]))
