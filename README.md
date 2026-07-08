# syn — synesthesia engine

音をLLMの解釈を通して色に変換する、モード宣言型のCLIエンジン。

- **research** — 再現可能な解釈。構造化ログ。分析と比較のためのモード。
- **live** — 一回性の解釈。ウィンドウに生成的パターンを描画するパフォーマンスモード。

モードは起動時にのみ宣言でき、セッション中に切り替えることはできない。

## Setup

```bash
python -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/pip install numpy sounddevice pygame  # audio + renderer
cp .env.example .env  # 値を編集
```

LLMはローカルの LM Studio または Ollama を使う（`SYN_LLM_PROVIDER`）。

## Usage

```bash
syn start research [--key KEY] [--seed N]
syn start live [--key KEY] [--session NAME]
```

- research: 1回の観測を解釈し、再現可能なログを `logs/research/` に書く
- live: ウィンドウが開き、解釈は数秒ごとに更新される。ESC または閉じるで終了。トレースは `logs/live/` へ

## Input sources（.env で選択・live モードのみ）

research モードは再現性のため常に固定入力（static）を観測する。以下は live モードに効く：

| 設定 | 値 | 意味 |
| --- | --- | --- |
| `SYN_INPUT_SOURCE` | `static`（デフォルト） | 固定のCメジャートライアド（開発・比較用） |
|  | `audio` | キャプチャデバイスを観測する |
| `SYN_AUDIO_DEVICE` | 未設定 | システムデフォルト入力 |
|  | デバイス名 or 番号 | 例: `BlackHole 2ch`、オーディオIFの入力 |
| `SYN_AUDIO_SAMPLE_RATE` | デフォルト `44100` | |
| `SYN_AUDIO_WINDOW_SECONDS` | デフォルト `2.0` | 観測ウィンドウ＝LLM解釈の周期 |

デバイス一覧: `.venv/bin/python -c "import sounddevice; print(sounddevice.query_devices())"`

**楽器（ベース/ギター）**: オーディオインターフェースの入力を `SYN_AUDIO_DEVICE` に指定。
**Mac内の音源（Music / TidalCycles / SuperCollider）**: BlackHole をインストールし、
「複数出力装置」（スピーカー＋BlackHole）をシステム出力にして `SYN_AUDIO_DEVICE=BlackHole 2ch`。

## Development

```bash
.venv/bin/python -m pytest tests/ --cov=syn
```

設計の哲学と構造は [CLAUDE.md](CLAUDE.md) を参照。プロンプトは `/prompts` が唯一の正。
