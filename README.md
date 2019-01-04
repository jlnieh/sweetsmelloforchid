[![Current Release](https://img.shields.io/github/release/jlnieh/sweetsmelloforchid.svg)](https://github.com/jlnieh/sweetsmelloforchid/releases/latest)
[![Github All Releases Downloads](https://img.shields.io/github/downloads/jlnieh/sweetsmelloforchid/total.svg?colorB=A9A9A9)](https://github.com/jlnieh/sweetsmelloforchid/releases/)

# 蘭畹清芬電子詩集製作計畫
這計畫預備幫聶懋戡先生已出版的兩本「蘭畹清芬」詩集進行電子化。

## 計畫目標
本計畫預計有三個目標，
1. 將現有於 1994 年和 1998 年出版的兩集「蘭畹清芬」簡體版詩集，進行掃描、轉換、與校對後，製作成 EPUB 格式的電子書。
2. 將這兩本簡體中文版的詩集，重行轉換回正體中文版詩集，並再與留存之手稿重行校對一次。
3. 蒐集、補錄聶懋戡先生生前手稿中尚未發表的作品，重新集結之後製作成新電子版詩集發行。

## 詩集下載
最新版的 EPUB 成品下載網頁：[releases page](https://github.com/jlnieh/sweetsmelloforchid/releases)

## 產生 EPUB
```
cookall.py -v vol01
cookall.py -v vol02
```

## Under the Hook
本計畫的詩詞原文來自於聶懋戡已出版的詩集印刷本，將印刷本掃描成圖檔之後，上傳至 Google Docs 進行 OCR 辨識轉成文字格式。然後，按盡量以原書章節，並配合 Markdown 格式儲存檔案，建立成詩詞資料庫。再配合事先準備的 templates，以 `cookall.py` 這隻小程式將詩詞本文轉換成 EPUB 所需的 xhtml 格式，並且集結成 EPUB 電子書。

## 著作授權 (License)
本計畫的著作授權分為下列部分，
* 聶懋戡先生詩集的內容中，聶懋戡本人的創作部分願採用 [![創用 CC 姓名標示 3.0 台灣 授權條款](https://i.creativecommons.org/l/by/3.0/tw/88x31.png)](https://creativecommons.org/licenses/by/3.0/tw//) 「[創用 CC 姓名標示 3.0 台灣 授權條款](https://creativecommons.org/licenses/by/3.0/tw//)」
* 詩集的內容中，非聶懋戡先生本人的創作部分，其著作權應歸原作者所有。
* 用來製作與產生電子書的軟體程式則採用 [![MIT license](https://img.shields.io/github/license/jlnieh/sweetsmelloforchid.svg)](LICENSE) [MIT license](LICENSE)。
