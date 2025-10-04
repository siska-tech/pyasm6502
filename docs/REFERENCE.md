# pyasm6502 リファレンスマニュアル

## 目次

1. [概要](#概要)
2. [インストールとセットアップ](#インストールとセットアップ)
3. [基本的な使用方法](#基本的な使用方法)
4. [CPUサポート](#cpuサポート)
5. [命令セット](#命令セット)
6. [疑似オペコード](#疑似オペコード)
7. [式と演算子](#式と演算子)
8. [シンボルとラベル](#シンボルとラベル)
9. [条件付きアセンブリ](#条件付きアセンブリ)
10. [ループ構造](#ループ構造)
11. [マクロシステム](#マクロシステム)
12. [ファイル管理](#ファイル管理)
13. [テキスト変換](#テキスト変換)
14. [セグメント管理](#セグメント管理)
15. [デバッグ機能](#デバッグ機能)
16. [出力形式](#出力形式)
17. [エラーハンドリング](#エラーハンドリング)
18. [ACMEとの互換性](#acmeとの互換性)
19. [トラブルシューティング](#トラブルシューティング)
20. [付録](#付録)

---

## 概要

pyasm6502は、ACME互換の6502アセンブラです。Pythonで実装されており、詳細なエラーレポートと現代的な開発体験を提供します。

### 主な特徴

- **ACME完全互換**: 100%のACME互換性（215/215テスト通過）
- **pipインストール対応**: 簡単な`pip install pyasm6502`でインストール可能
- **詳細なエラーレポート**: ソースコード行の視覚的表示
- **モジュラー設計**: 保守性と拡張性を重視
- **型安全性**: Pythonの型ヒントを活用
- **クロスプラットフォーム**: Pythonが動作するすべての環境
- **MITライセンス**: 商用利用可能なオープンソースライセンス

### ACMEとの比較

| 項目 | ACME | pyasm6502 |
|------|------|---------|
| **実装言語** | C | Python |
| **ライセンス** | GNU GPL v2.0 | MIT License |
| **CPUサポート** | 9種類 | 4種類 |
| **エラーレポート** | 基本 | 詳細（視覚的） |
| **保守性** | 中程度 | 高 |
| **パフォーマンス** | 高速 | 中程度 |

---

## インストールとセットアップ

### 必要条件

- Python 3.7以上
- 外部依存関係なし

### インストール方法

#### 1. pipインストール（推奨）

```bash
# PyPIからインストール
pip install pyasm6502
```

#### 2. ソースからインストール

```bash
# リポジトリをクローン
git clone https://github.com/siska-tech/pyasm6502.git
cd pyasm6502

# インストール
pip install .
```

#### 3. 開発用インストール

```bash
# エディタブルインストール（開発用）
pip install -e .

# 開発依存関係を含めてインストール
pip install -e ".[dev]"
```

### 基本動作確認

```bash
# インストール確認
pyasm6502 --help

# テスト実行
cd tests
python quick_test.py
python run_tests.py
```

---

## 基本的な使用方法

### コマンドライン構文

```bash
pyasm6502 [オプション] 入力ファイル
```

### オプション

| オプション | 説明 | 例 |
|------------|------|-----|
| `-o`, `--output` | 出力ファイル名 | `-o program.bin` |
| `-f`, `--format` | 出力形式 | `-f hex` |
| `-l`, `--list` | リスティングファイル生成 | `-l program.lst` |
| `-s`, `--symbols` | シンボルテーブル表示 | `-s` |
| `--setpc` | プログラムカウンタ設定 | `--setpc $C000` |
| `-I`, `--include` | インクルードパス追加 | `-I include_dir` |
| `-v`, `--verbose` | 詳細レベル | `-v2` |
| `--vicelabels` | VICEラベルファイル生成 | `--vicelabels labels.vl` |

### 使用例

#### pipインストール後の使用

```bash
# 基本的なアセンブリ
pyasm6502 program.a

# Intel HEX形式で出力
pyasm6502 -f hex -o program.hex program.a

# インクルードディレクトリを指定
pyasm6502 -I include_dir -I lib_dir program.a

# 詳細な出力でデバッグ
pyasm6502 -v2 -s program.a

# プログラムカウンタを設定
pyasm6502 --setpc $C000 program.a

# VICEデバッガー用ラベルファイル生成
pyasm6502 --vicelabels labels.vice program.a
```

#### ソースから直接実行

```bash
# 基本的なアセンブリ
python pyasm6502/asm6502.py program.a

# Intel HEX形式で出力
python pyasm6502/asm6502.py -f hex -o program.hex program.a

# インクルードディレクトリを指定
python pyasm6502/asm6502.py -I include_dir -I lib_dir program.a

# 詳細な出力でデバッグ
python pyasm6502/asm6502.py -v2 -s program.a
```

---

## CPUサポート

### サポート対象CPU

| CPU | 説明 | ACMEとの比較 |
|-----|------|-------------|
| **6502** | オリジナルMOS Technology 6502 | ✅ 同等 |
| **65C02** | CMOS 6502 | ✅ 同等 |
| **NMOS6502** | NMOS 6502（違法オペコード含む） | ✅ 同等 |
| **W65C02S** | Western Design Center 65C02 | ❌ ACME未対応 |

### CPU指定

```assembly
!cpu 6502        ; デフォルト
!cpu 65c02       ; CMOS 6502
!cpu nmos6502    ; NMOS 6502（違法オペコード有効）
!cpu w65c02      ; W65C02S
```

### ACMEでサポートされているがpyasm6502で未対応のCPU

- 65816
- 65ce02
- 4502
- MEGA65

**注意**: これらのCPUが必要な場合はACMEの使用を推奨します。

---

## 命令セット

### 基本的な命令

#### ロード・ストア命令

```assembly
LDA #$42        ; 即値ロード
LDA $2000       ; 絶対アドレス
LDA $20         ; ゼロページ
LDA $20,X       ; ゼロページ+X
LDA $2000,X     ; 絶対+X
LDA $2000,Y     ; 絶対+Y
LDA ($20,X)     ; インデックス間接
LDA ($20),Y     ; 間接インデックス

STA $2000       ; ストア（同様のアドレシングモード）
STX $20         ; Xレジスタストア
STY $20         ; Yレジスタストア
```

#### 転送命令

```assembly
TAX             ; A → X
TAY             ; A → Y
TXA             ; X → A
TYA             ; Y → A
TSX             ; SP → X
TXS             ; X → SP
```

#### スタック操作

```assembly
PHA             ; Aをプッシュ
PLA             ; Aをポップ
PHP             ; フラグをプッシュ
PLP             ; フラグをポップ
```

#### 算術演算

```assembly
ADC #$10        ; 加算（キャリー込み）
SBC #$10        ; 減算（ボロー込み）
INC $2000       ; インクリメント
DEC $2000       ; デクリメント
INX             ; Xをインクリメント
INY             ; Yをインクリメント
DEX             ; Xをデクリメント
DEY             ; Yをデクリメント
```

#### 論理演算

```assembly
AND #$0F        ; 論理積
ORA #$80        ; 論理和
EOR #$FF        ; 排他的論理和
```

#### 比較・分岐

```assembly
CMP #$42        ; Aと比較
CPX #$10        ; Xと比較
CPY #$20        ; Yと比較

BEQ label       ; 等しい場合分岐
BNE label       ; 等しくない場合分岐
BCC label       ; キャリークリア時分岐
BCS label       ; キャリーセット時分岐
BMI label       ; マイナス時分岐
BPL label       ; プラス時分岐
BVS label       ; オーバーフローセット時分岐
BVC label       ; オーバーフロークリア時分岐
```

### CPU固有命令

#### 65C02固有

```assembly
BRA label       ; 無条件分岐
PHX             ; Xをプッシュ
PLX             ; Xをポップ
PHY             ; Yをプッシュ
PLY             ; Yをポップ
STZ $2000       ; ゼロストア
TRB $2000       ; テスト・リセット・ビット
TSB $2000       ; テスト・セット・ビット
```

#### W65C02S固有

```assembly
WAI             ; 割り込み待機
STP             ; ストップ
SMB0 $20        ; セット・ビット（0-7）
RMB0 $20        ; リセット・ビット（0-7）
BBR0 $20,label  ; ブランチ・ビット・リセット
BBS0 $20,label  ; ブランチ・ビット・セット
```

#### NMOS6502違法オペコード

```assembly
LAX #$42        ; ロード・A・X
SAX $2000       ; ストア・A・X
DCP $2000       ; デクリメント・比較
ISB $2000       ; インクリメント・減算
SLO $2000       ; シフト・ロジック・OR
RLA $2000       ; ローテート・ロジック・AND
SRE $2000       ; シフト・排他的論理和
RRA $2000       ; ローテート・右・加算
```

---

## 疑似オペコード

### データ定義

```assembly
!byte $42, $43, $44    ; バイトデータ
!word $1234, $5678     ; ワードデータ（リトルエンディアン）
!8 $42                 ; 8ビットデータ
!16 $1234              ; 16ビットデータ
!24 $123456            ; 24ビットデータ
!32 $12345678          ; 32ビットデータ

!8be $1234             ; 8ビット（ビッグエンディアン）
!16be $1234            ; 16ビット（ビッグエンディアン）
!24be $123456          ; 24ビット（ビッグエンディアン）
!32be $12345678        ; 32ビット（ビッグエンディアン）

!hex "1234ABCD"        ; 16進文字列
!skip 256              ; スキップ（0で埋める）
!align 256             ; アライメント
```

### 文字列定義

```assembly
!pet "Hello"           ; PETSCII文字列
!scr "HELLO"           ; スクリーンコード文字列
!text "Hello"          ; テキスト文字列
```

### ACMEとの互換性

| 疑似オペコード | ACME | pyasm6502 | 備考 |
|---------------|------|---------|------|
| `!byte` | ✅ | ✅ | 完全互換 |
| `!word` | ✅ | ✅ | 完全互換 |
| `!8`, `!16`, `!24`, `!32` | ✅ | ✅ | 完全互換 |
| `!hex` | ✅ | ✅ | 完全互換 |
| `!skip` | ✅ | ✅ | 完全互換 |
| `!align` | ✅ | ✅ | 完全互換 |
| `!pet` | ✅ | ✅ | 完全互換 |
| `!scr` | ✅ | ✅ | 完全互換 |

---

## 式と演算子

### 数値表現

```assembly
$1234          ; 16進数
%10101010      ; 2進数
1234           ; 10進数
'@'            ; 文字定数
```

### 演算子

#### 算術演算子

```assembly
+              ; 加算
-              ; 減算
*              ; 乗算
/              ; 除算
%              ; 剰余
**             ; べき乗
```

#### ビット演算子

```assembly
&              ; ビットAND
|              ; ビットOR
^              ; ビットXOR
~              ; ビットNOT
<<             ; 左シフト
>>             ; 右シフト
```

#### 比較演算子

```assembly
==             ; 等しい
!=             ; 等しくない
<>             ; 等しくない（ACME互換）
<              ; より小さい
>              ; より大きい
<=             ; 以下
>=             ; 以上
```

#### 論理演算子

```assembly
&&             ; 論理AND
||             ; 論理OR
!              ; 論理NOT
```

### 演算子優先度

| 優先度 | 演算子 | 説明 |
|--------|--------|------|
| 1 | `!`, `~` | 単項演算子 |
| 2 | `**` | べき乗 |
| 3 | `*`, `/`, `%` | 乗除算 |
| 4 | `+`, `-` | 加減算 |
| 5 | `<<`, `>>` | シフト |
| 6 | `<`, `>`, `<=`, `>=` | 比較 |
| 7 | `==`, `!=`, `<>` | 等価性 |
| 8 | `&` | ビットAND |
| 9 | `^` | ビットXOR |
| 10 | `\|` | ビットOR |
| 11 | `&&` | 論理AND |
| 12 | `\|\|` | 論理OR |

### 組み込み関数

#### 数学関数

```assembly
sin(angle)     ; サイン
cos(angle)     ; コサイン
tan(angle)     ; タンジェント
arcsin(value)  ; アークサイン
arccos(value)  ; アークコサイン
arctan(value)  ; アークタンジェント
int(value)     ; 整数変換
float(value)   ; 浮動小数点変換
```

#### 型チェック関数

```assembly
is_number(value)   ; 数値チェック
is_list(value)     ; リストチェック
is_string(value)   ; 文字列チェック
len(value)         ; 長さ取得
```

### 使用例

```assembly
; 複雑な式の例
value = ($1000 + $2000) * 2 + sin(angle) & $FF
result = (value > 100) && (value < 200)
```

---

## シンボルとラベル

### ラベル定義

```assembly
; グローバルラベル
start:
    lda #$42

; ローカルラベル（.で始まる）
.local_label:
    sta $2000

; 安価なローカルラベル（@で始まる）
@loop:
    dex
    bne @loop

; 匿名ラベル
    lda #$10
+   bne +
    lda #$20
-   bne -
    rts
```

### シンボル定義

```assembly
; 定数定義
CLEAR = 147
SCREEN = $0400

; 変数定義（!setディレクティブ）
!set counter = 0
!set max_count = 100
```

### ゾーンシステム

```assembly
; ゾーン定義
!zone main
.local_var:
    lda #$42

!zone subroutines
.local_var:         ; 異なるゾーンの同じ名前
    rts
```

### ACMEとの互換性

| 機能 | ACME | pyasm6502 | 備考 |
|------|------|---------|------|
| グローバルラベル | ✅ | ✅ | 完全互換 |
| ローカルラベル | ✅ | ✅ | 完全互換 |
| 匿名ラベル | ✅ | ✅ | 完全互換 |
| 安価なローカル | ✅ | ✅ | 完全互換 |
| ゾーンシステム | ✅ | ✅ | 完全互換 |

---

## 条件付きアセンブリ

### 基本的な条件文

```assembly
!if value == 1
    lda #$42
!else
    lda #$00
!fi

; シンボル存在チェック
!ifdef SYMBOL_NAME
    ; シンボルが定義されている場合
!else
    ; シンボルが定義されていない場合
!fi

!ifndef DEBUG
    ; デバッグモードでない場合
!fi
```

### 複雑な条件

```assembly
!if (value > 100) && (value < 200)
    ; 複合条件
!fi

!if cpu == "65c02"
    ; CPU固有コード
!elseif cpu == "w65c02"
    ; 別のCPU固有コード
!else
    ; デフォルトコード
!fi
```

### ネストした条件

```assembly
!if condition1
    !if condition2
        ; ネストした条件
    !else
        ; 内側のelse
    !fi
!else
    ; 外側のelse
!fi
```

---

## ループ構造

### FORループ

```assembly
!for i = 0 to 9
    !byte i
!next

; ステップ指定
!for i = 0 to 100 step 10
    !word i * 2
!next
```

### WHILEループ

```assembly
!set counter = 0
!while counter < 10
    !byte counter
    !set counter = counter + 1
!wend
```

### DO-WHILEループ

```assembly
!set counter = 0
!do
    !byte counter
    !set counter = counter + 1
!until counter >= 10
```

### ループ制御

```assembly
!for i = 0 to 100
    !if i == 50
        !break          ; ループ終了
    !fi
    !if i == 25
        !continue       ; 次の反復へ
    !fi
    !byte i
!next
```

---

## マクロシステム

### マクロ定義

```assembly
!macro print_string string_addr
    ldx #0
-   lda string_addr, x
    beq +
    jsr $ffd2
    inx
    bne -
+   rts
!endmacro
```

### マクロ呼び出し

```assembly
; マクロ呼び出し
+print_string message1
+print_string message2

message1:
    !pet "Hello", 0
message2:
    !pet "World", 0
```

### パラメータ付きマクロ

```assembly
!macro add_immediate value, address
    lda #value
    clc
    adc address
    sta address
!endmacro

+add_immediate 10, counter
+add_immediate 5, score
```

### デフォルトパラメータ

```assembly
!macro delay cycles=100
    !for i = 0 to cycles - 1
        nop
    !next
!endmacro

+delay              ; デフォルト100サイクル
+delay 50           ; 50サイクル
```

---

## ファイル管理

### ファイルインクルード

```assembly
!source "header.a"      ; ファイルインクルード
!src "macros.a"         ; 別名

; インクルードパス指定
!source "lib/math.a"
!source "../common/defs.a"
```

### バイナリファイルインクルード

```assembly
!binary "data.bin"      ; バイナリファイル
!bin "sprite.dat"       ; 別名
```

### ファイル検索パス

```assembly
; コマンドラインで指定
pyasm6502 -I include_dir -I lib_dir program.a

; プログラム内でも設定可能
!source "header.a"      ; include_dirから検索
```

---

## テキスト変換

### 変換テーブル定義

```assembly
!convtab "pet2iso.bin"  ; 変換テーブル指定
!ct "custom.tab"        ; 別名
```

### 文字列変換

```assembly
!scr "HELLO"            ; スクリーンコード
!scrxor $80, "hello"    ; XOR変換
```

### 組み込み変換テーブル

```assembly
; PETSCII → ISO変換
!convtab "pet2iso.bin"

; カスタム変換テーブル
!convtab "my_table.bin"
```

---

## セグメント管理

### 疑似PC設定

```assembly
!pseudopc $8000
    ; このセクションは$8000に配置される
    lda #$42
    sta $2000
!realpc
    ; 実際のPCに戻る
```

### メモリ初期化

```assembly
!initmem $FF           ; 未使用メモリを$FFで初期化
!initmem 0             ; 0で初期化
```

### XOR変換

```assembly
!xor $AA               ; 出力バイトを$AAでXOR
```

---

## デバッグ機能

### 警告・エラー出力

```assembly
!warn "This is a warning message"
!error "This is an error message"
!serious "This is a serious error"
```

### シンボルリスト出力

```assembly
!symbollist "symbols.txt"  ; シンボルリスト出力
!sl "symbols.txt"          ; 別名
```

### デバッグレベル設定

```bash
# コマンドラインで詳細レベル指定
pyasm6502 -v2 program.a

# レベル1: 通常
# レベル2: 詳細
# レベル3: デバッグ
```

---

## 出力形式

### 対応出力形式

| 形式 | 説明 | 拡張子 |
|------|------|--------|
| **plain** | プレーンバイナリ | .bin |
| **cbm** | CBM形式（ロードアドレス付き） | .prg |
| **apple** | Apple II形式 | .bin |
| **hex** | Intel HEX形式 | .hex |

### 出力例

```bash
# プレーンバイナリ
pyasm6502 -f plain -o program.bin program.a

# CBM形式
pyasm6502 -f cbm -o program.prg program.a

# Intel HEX形式
pyasm6502 -f hex -o program.hex program.a
```

### VICEラベルファイル

```bash
# VICEデバッガ用ラベルファイル生成
pyasm6502 --vicelabels labels.vl program.a
```

---

## エラーハンドリング

### エラーメッセージ形式

```
Error - File program.a, line 15: Undefined symbol: undefined_label
  LDA undefined_label ; This line has an error
  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

### エラータイプ

| エラータイプ | 説明 | 例 |
|-------------|------|-----|
| **Undefined Symbol** | 未定義シンボル | `LDA undefined_label` |
| **Syntax Error** | 構文エラー | `LDA #$` |
| **Addressing Mode** | アドレシングモードエラー | `LDA #$42, X` |
| **Range Error** | 範囲エラー | `LDA #$1234` (8ビット値) |
| **File Error** | ファイルエラー | `!source "missing.a"` |

### エラーレポートの特徴

- **視覚的表示**: エラー行を矢印で指摘
- **詳細情報**: ファイル名、行番号、エラー内容
- **コンテキスト**: エラー周辺のコード表示

### ACMEとの比較

| 項目 | ACME | pyasm6502 |
|------|------|---------|
| **エラーメッセージ** | 基本 | 詳細 |
| **視覚的表示** | ❌ | ✅ |
| **コンテキスト** | 限定的 | 豊富 |
| **デバッグ支援** | 中程度 | 高 |

---

## ACMEとの互換性

### 完全互換機能

- ✅ 命令セット（サポート対象CPU）
- ✅ 疑似オペコード
- ✅ 式と演算子
- ✅ シンボルシステム
- ✅ 条件付きアセンブリ
- ✅ ループ構造
- ✅ マクロシステム
- ✅ ファイル管理
- ✅ テキスト変換
- ✅ セグメント管理

### 拡張機能

- 🔥 詳細なエラーレポート
- 🔥 W65C02S CPUサポート
- 🔥 視覚的デバッグ支援
- 🔥 型安全性

### 制限事項

| 機能 | 状況 | 対処法 |
|------|------|--------|
| **65816 CPU** | 未対応 | ACMEを使用 |
| **MEGA65 CPU** | 未対応 | ACMEを使用 |
| **65ce02 CPU** | 未対応 | ACMEを使用 |

### 移行ガイド

#### ACMEからpyasm6502へ

1. **ファイル拡張子**: `.a`のまま使用可能
2. **構文**: 変更不要
3. **CPU指定**: サポート対象CPUのみ
4. **エラーレポート**: より詳細な情報を活用

#### 移行例

```assembly
; ACMEコード
!cpu 6502
* = $c000
start:
    lda #$42
    sta $2000
    rts

; pyasm6502でも同じコードが動作
!cpu 6502
* = $c000
start:
    lda #$42
    sta $2000
    rts
```

---

## トラブルシューティング

### よくある問題

#### 1. 未定義シンボルエラー

```
Error - File program.a, line 10: Undefined symbol: my_label
```

**解決法**:
- ラベルが正しく定義されているか確認
- 大文字小文字の区別を確認
- ゾーンの範囲を確認

#### 2. CPU固有命令エラー

```
Error - File program.a, line 5: Unknown instruction: WAI
```

**解決法**:
```assembly
!cpu w65c02      ; 正しいCPUを指定
```

#### 3. ファイルが見つからない

```
Error - File program.a, line 3: File not found: header.a
```

**解決法**:
- ファイルパスを確認
- インクルードパスを指定: `pyasm6502 -I include_dir program.a`

#### 4. 構文エラー

```
Error - File program.a, line 8: Syntax error: unexpected token
```

**解決法**:
- 括弧の対応を確認
- 演算子の優先度を確認
- 文字列の引用符を確認

### デバッグのコツ

1. **詳細レベルを上げる**: `-v2`または`-v3`オプション
2. **シンボルテーブルを確認**: `-s`オプション
3. **リスティングファイル生成**: `-l`オプション
4. **エラーメッセージを詳しく読む**: 視覚的表示を活用

### インストール関連の問題

#### 5. pyasm6502コマンドが見つからない

```
'pyasm6502' is not recognized as an internal or external command
```

**解決法**:
- pipでインストール: `pip install pyasm6502`
- PATHにPython Scriptsディレクトリが含まれているか確認
- 仮想環境を使用している場合は有効化を確認

#### 6. モジュールインポートエラー

```
ModuleNotFoundError: No module named 'pyasm6502'
```

**解決法**:
- パッケージを再インストール: `pip uninstall pyasm6502 && pip install pyasm6502`
- 正しいPython環境を使用しているか確認
- 開発用インストール: `pip install -e .`

### パフォーマンス最適化

1. **不要なインクルードを避ける**
2. **大きなループは最小限に**
3. **マクロの使用を適切に**
4. **メモリ使用量を監視**

---

## 付録

### A. 命令セット一覧

#### 6502基本命令

| ニーモニック | アドレシング | オペコード | サイズ |
|-------------|-------------|-----------|--------|
| LDA | IMM | $A9 | 2 |
| LDA | ZP | $A5 | 2 |
| LDA | ZPX | $B5 | 2 |
| LDA | ABS | $AD | 3 |
| LDA | ABSX | $BD | 3 |
| LDA | ABSY | $B9 | 3 |
| LDA | INDX | $A1 | 2 |
| LDA | INDY | $B1 | 2 |

#### 65C02追加命令

| ニーモニック | アドレシング | オペコード | サイズ |
|-------------|-------------|-----------|--------|
| BRA | REL | $80 | 2 |
| PHX | IMP | $DA | 1 |
| PLX | IMP | $FA | 1 |
| PHY | IMP | $5A | 1 |
| PLY | IMP | $7A | 1 |
| STZ | ZP | $64 | 2 |
| STZ | ABS | $9C | 3 |

### B. 疑似オペコード一覧

| 疑似オペコード | 説明 | 例 |
|---------------|------|-----|
| `!byte` | バイトデータ | `!byte $42, $43` |
| `!word` | ワードデータ | `!word $1234` |
| `!8` | 8ビットデータ | `!8 $42` |
| `!16` | 16ビットデータ | `!16 $1234` |
| `!24` | 24ビットデータ | `!24 $123456` |
| `!32` | 32ビットデータ | `!32 $12345678` |
| `!hex` | 16進文字列 | `!hex "1234ABCD"` |
| `!skip` | スキップ | `!skip 256` |
| `!align` | アライメント | `!align 256` |
| `!pet` | PETSCII文字列 | `!pet "Hello"` |
| `!scr` | スクリーンコード | `!scr "HELLO"` |

### C. 演算子一覧

| 演算子 | 説明 | 優先度 |
|--------|------|--------|
| `!` | 論理NOT | 1 |
| `~` | ビットNOT | 1 |
| `**` | べき乗 | 2 |
| `*` | 乗算 | 3 |
| `/` | 除算 | 3 |
| `%` | 剰余 | 3 |
| `+` | 加算 | 4 |
| `-` | 減算 | 4 |
| `<<` | 左シフト | 5 |
| `>>` | 右シフト | 5 |
| `<` | より小さい | 6 |
| `>` | より大きい | 6 |
| `<=` | 以下 | 6 |
| `>=` | 以上 | 6 |
| `==` | 等しい | 7 |
| `!=` | 等しくない | 7 |
| `<>` | 等しくない | 7 |
| `&` | ビットAND | 8 |
| `^` | ビットXOR | 9 |
| `\|` | ビットOR | 10 |
| `&&` | 論理AND | 11 |
| `\|\|` | 論理OR | 12 |

### D. 組み込み関数一覧

#### 数学関数

| 関数 | 説明 | 例 |
|------|------|-----|
| `sin(angle)` | サイン | `sin(3.14159/2)` |
| `cos(angle)` | コサイン | `cos(0)` |
| `tan(angle)` | タンジェント | `tan(0.785398)` |
| `arcsin(value)` | アークサイン | `arcsin(1.0)` |
| `arccos(value)` | アークコサイン | `arccos(0.0)` |
| `arctan(value)` | アークタンジェント | `arctan(1.0)` |
| `int(value)` | 整数変換 | `int(3.14)` |
| `float(value)` | 浮動小数点変換 | `float(42)` |

#### 型チェック関数

| 関数 | 説明 | 例 |
|------|------|-----|
| `is_number(value)` | 数値チェック | `is_number(42)` |
| `is_list(value)` | リストチェック | `is_list([1,2,3])` |
| `is_string(value)` | 文字列チェック | `is_string("hello")` |
| `len(value)` | 長さ取得 | `len("hello")` |

### E. リソース

- **公式リポジトリ**: [GitHub Repository]
- **ACME公式**: [ACME Assembler]
- **6502リファレンス**: [6502.org]
- **VICE エミュレータ**: [VICE Emulator]

---

*このマニュアルはpyasm6502の完全なリファレンスです。ACMEとの互換性を保ちながら、pyasm6502の独自機能も活用してください。*