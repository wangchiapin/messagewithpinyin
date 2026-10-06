"""把 template.html、engine.js、函式庫和 GoodTeacher 規則組合成網站用的 index.html。

用法（在 src 資料夾裡執行）：
    python3 build.py
產生的檔案：../index.html（簡→繁字典 ../opencc-cn2t.js 已經在 repo 根目錄，不用重做）
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'index.html')


def read(name):
    with open(os.path.join(HERE, name), encoding='utf8') as f:
        return f.read()


def main():
    t = read('template.html')
    for key, f in [('/*__PINYIN_PRO__*/', 'lib-pinyin-pro.js'), ('/*__T2CN__*/', 'lib-t2cn.js'), ('/*__ENGINE__*/', 'engine.js')]:
        c = read(f)
        assert '</script' not in c.lower(), f
        assert key in t, key
        t = t.replace(key, c, 1)
    gt = read('gt-rules.json')
    json.loads(gt)  # 確認格式正確
    assert '</script' not in gt.lower()
    t = t.replace('/*__GT_RULES__*/null', gt, 1)
    with open(OUT, 'w', encoding='utf8') as f:
        f.write(t)
    print('built', os.path.normpath(OUT), len(t.encode('utf8')) // 1024, 'KB')


if __name__ == '__main__':
    main()
