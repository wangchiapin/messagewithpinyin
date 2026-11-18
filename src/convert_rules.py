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
    '哥': 'gē', '姐': 'jiě', '姊': 'jiě', '弟': 'dì', '妹': 'mèi', '叔': 'shú',
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
    ('吐', '1'): 'tù', ('发', '2'): 'fǎ',
}
KIN = '媽妈爸爺爷奶哥姐姊弟妹叔舅姑婆公娃寶宝嫂爹娘嬸婶伯'
for c in KIN:
    IDX[(c, '1')] = neutral(DEFAULT[c])


def seq(field):
    """'星|期' → ['星', '期']；'@GT_HANZI' 保留成代號。"""
    return [p for p in field.split('|')] if field else []


def load_gt_table(path):
    """讀 GoodTeacher 的 readings.txt：回傳 (字→讀音編號清單, 編號→拼音)。"""
    lab, chr_, sec = {}, {}, ''
    for ln in open(path, encoding='utf-8-sig').read().splitlines():
        if ln == '[L]': sec = 'L'; continue
        if ln == '[C]': sec = 'C'; continue
        i = ln.find('=')
        if i < 0: continue
        if sec == 'L': lab[ln[:i]] = ln[i+1:].split(' ')[0]
        elif sec == 'C': chr_[ln[:i]] = ln[i+1:].split(',')
    return chr_, lab


def main(src, dst, readings=None, classes_path=None):
    rows = list(csv.DictReader(open(src, encoding='utf-8-sig')))
    # 表裡沒寫的字，直接查 GoodTeacher 的讀音表（readings.txt 和 rules.csv 同一版）
    chr_, lab = load_gt_table(readings) if readings else ({}, {})
    classes = {}
    if classes_path:
        for ln in open(classes_path, encoding='utf-8-sig').read().splitlines():
            i = ln.find('=')
            if i > 0: classes[ln[:i]] = ln[i+1:]
    def from_table(ch, slot):
        rs = chr_.get(ch)
        if not rs: return None
        try: code = rs[int(slot)]
        except (ValueError, IndexError): return None
        return unicodedata.normalize('NFC', lab.get(code, code))
    out, problems = [], []
    # GT_SDEF：簡體字的預設字形若改用第 k 個讀音（例：夹 → jiá），網頁的「預設讀音」也要照它
    SDEF_SLOT = {r['字']: int(r['讀音編號']) for r in rows if r['群組'] == 'GT_SDEF' and r['動作'] == '改' and not r['前文'] and not r['後文'] and r['讀音編號'].isdigit()}
    for n, r in enumerate(rows, start=2):
        if r['群組'] in SKIP_GROUPS and not (r['群組'] == 'GT_SIMP9' and r['字'] == '脏') and not (r['群組'] == 'GT_SDEF' and r['字'] in ('缝', '铺')):   # 脏：心脏念 zàng、其餘念 zāng；缝／铺：整組規則（含最後的預設 féng／pū）網頁要照字體，否則 pinyin-pro 會把裁缝讀成 fèng
            continue
        ch = r['字']
        if r['動作'] == '不改':
            py = DEFAULT.get(ch) or from_table(ch, 0)
        else:
            py = r['讀音提示'].strip() or IDX.get((ch, r['讀音編號'])) or from_table(ch, r['讀音編號'])
        if not py:
            problems.append(f'第 {n} 行：{ch} 編號 {r["讀音編號"]} 找不到讀音')
            continue
        out.append([ch, py, seq(r['前文']), seq(r['後文'])])
    # 沒有規則、但 pinyin-pro 會讀錯的字：直接用 GoodTeacher 的預設讀音（只收人工確認過的字；要加字，先確認 GoodTeacher 預設沒錯）
    VETTED = '息熄惜擊播巍乾績識只誰髮寧究暫儲檔艘飩微椰獺嗯欸調夾夹炸切築筑臟麗丽廈厦饨縫缝绩暂识击储档喔遛啦卡谁質质框角綜综企熟當当曳跡迹捲模跌夕蹈突擁拥殼勁劲傍括耶仔鋪铺載载獲幹帆簿淑妳驟骤桿唉悄喲哟蹟鑽钻間间'   # 绩暂识击储档：繁體已確認的字的簡體寫法（GT_SDEF 預設）
    vetted = {}
    for ch in VETTED:
        v = from_table(ch, SDEF_SLOT.get(ch, 0))
        if v: vetted[ch] = v
    # 一／不 看下一字的聲調：GT 的類別（classes.txt）裡有些字預設是輕聲、卻歸在四聲類（例：个 → 一个 yí）。
    # 引擎只看拼音會把這些字當輕聲，所以另外給「輕聲字 → GT 類別的聲調」。
    neu_tone = {}
    if classes:
        for cname, tone in (('T4YI', 4), ('T123YI', 1)):
            for ch in classes.get(cname, ''):
                rs = chr_.get(ch)
                if not rs: continue
                v = from_table(ch, 0)
                if v and not any(c in v for c in 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ') and ch not in neu_tone:
                    neu_tone[ch] = tone
    json.dump({'rules': out, 'defaults': DEFAULT, 'vetted': vetted, 'neuTone': neu_tone}, open(dst, 'w', encoding='utf-8'),
              ensure_ascii=False, separators=(',', ':'))
    print(f'{len(out)} 條規則寫入 {dst}')
    for p in problems:
        print('!!', p)
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None, sys.argv[4] if len(sys.argv) > 4 else None))
