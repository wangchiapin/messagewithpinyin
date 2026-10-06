# 漢字加拼音：原始檔

網站只用到 repo 根目錄的 `index.html` 和 `opencc-cn2t.js`。這個資料夾放的是產生 `index.html` 的原始檔，改功能時改這裡，再重新組合。

| 檔案 | 用途 |
| --- | --- |
| `template.html` | 網頁的樣子、按鈕、畫圖片（canvas）的程式 |
| `engine.js` | 讀音判斷：台灣讀音、GoodTeacher 語境規則、一／不變調、拼音轉注音、文字版輸出 |
| `gt-rules.json` | 由 GoodTeacher 的 `rules.csv` 轉出來的語境規則（574 條） |
| `convert_rules.py` | 把 `rules.csv` 轉成 `gt-rules.json` |
| `build.py` | 把上面這些和函式庫組合成 `../index.html` |
| `lib-pinyin-pro.js` | 拼音字典函式庫 pinyin-pro 3.29.4（MIT） |
| `lib-t2cn.js` | 繁→簡轉換 opencc-js 1.4.2（MIT）；`../opencc-cn2t.js` 是簡→繁 |
| `test-engine.js`, `words.txt` | 在 Node 裡測讀音：`node test-engine.js 銀行 一個人` |

## 更新 GoodTeacher 規則

`rules.csv` 沒有放在這裡。拿到新的 `rules.csv` 後：

```
python3 convert_rules.py 路徑/rules.csv gt-rules.json
python3 build.py
```

`convert_rules.py` 裡的 `DEFAULT` 和 `IDX` 是 ToneOZ 讀音編號對應的讀音；CSV 出現沒對應到的編號時，轉換會列出來並失敗。

## 改完要測

```
node test-engine.js          # 跑 words.txt 裡的詞
node test-engine.js 你和我 倒下
```
