[EN](README.md) | [DE](README_de.md) | [ES](README_es.md) | **JA** | [RU](README_ru.md) | [ZH](README_zh-Hans.md)

# connectors

Telegram、Discord、Signal、WhatsApp、Home Assistant、汎用 HTTP Webhook に対応した
スタンドアロン Python メッセージングコネクターモジュール。

[BACH](../../.AI/.OS/BACH/) (`.OS/BACH/system/connectors/`) から抽出・分離。
フレームワーク不要。必須の外部依存関係なし（標準ライブラリのみ）。

> **ステータス:** v1.0.0 — 動作確認済み、独立パッケージとしての公開は未実施。
> 計画中の改善点は [TODO.md](TODO.md) を参照。

## 対応コネクター

| コネクター      | プロトコル            | 出典                        | ステータス |
|-----------------|-----------------------|-----------------------------|----------|
| `telegram`      | Telegram Bot API      | BACH からポート             | 安定     |
| `discord`       | Discord Bot + Webhook | BACH からポート             | 安定     |
| `signal`        | signal-cli            | BACH からポート             | 安定     |
| `whatsapp`      | WhatsApp Business API | BACH からポート             | 安定     |
| `homeassistant` | Home Assistant REST   | BACH からポート             | 安定     |
| `webhook`       | 汎用 HTTP POST        | 新規（BACH に同等品なし）   | スタブ   |

`webhook` コネクターは**新規追加**です — 以前の計画書に記載されていましたが
BACH には存在しませんでした。基本的な送信専用 HTTP POST コネクターとして動作し、
スタブ/ベースラインとして明示的にマークされています。

## クイックスタート

```python
import os
from connectors import create_connector, ConnectorConfig

# Telegram の例
config = ConnectorConfig(
    name="my_bot",
    connector_type="telegram",
    auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]},
    options={"owner_chat_id": ""},   # オプション: このチャットのみ受信
)
conn = create_connector(config)
if conn.connect():
    conn.send_message("CHAT_ID", "こんにちは!")

# メッセージ受信（ポーリング）
thread, stop = conn.poll_threaded(on_message=lambda m: print(m.content))
# ... 後で:
stop.set()
```

## シークレット管理

**トークンをコードに直書きしないでください。** 推奨される方法:

```python
# 1. 環境変数（最もシンプル）
auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]}

# 2. python-dotenv
from dotenv import load_dotenv; load_dotenv()
auth_config={"bot_token": os.getenv("TG_BOT_TOKEN")}

# 3. SecretAdapter（フレームワーク統合、例: BACH）
from connectors.base import SecretAdapter

class MyAdapter(SecretAdapter):
    def get_secret(self, key: str) -> str:
        return my_vault.get(key, "")

conn = create_connector(config, secret_adapter=MyAdapter())
```

## カスタムコネクターの作成

対話型ウィザードを使用:

```bash
pip install pyyaml   # ウィザードのみ必要
python -m connectors.templates.setup_wizard
```

または `templates/connector_template.py` を使って手動で:

1. `connector_template.py` を `my_connector.py` にコピー
2. すべての `{{PLACEHOLDER}}` マーカーを置換
3. `connect()`、`disconnect()`、`send_message()`、`get_messages()` を実装
4. `__init__.py` の `_CONNECTOR_MAP` に登録

## BACH 統合（オプション）

このモジュールを BACH 内で使用するには、`hub.secrets_handler.SecretsHandler` を
指す `SecretAdapter` を実装します:

```python
from connectors.base import SecretAdapter

class BachSecretAdapter(SecretAdapter):
    def get_secret(self, key: str) -> str:
        try:
            from hub.secrets_handler import SecretsHandler
            return SecretsHandler().get_secret(key) or ""
        except ImportError:
            return ""
```

BACH はその後、オプションでこのモジュールに `connectors/` レイヤーを切り替えられます。
詳細は [BACH-REIMPORT-NOTE.md](BACH-REIMPORT-NOTE.md) を参照。

## プロジェクト構成

```
connectors/
├── __init__.py                  # create_connector() ファクトリ
├── base.py                      # BaseConnector, Message, SecretAdapter
├── telegram_connector.py
├── discord_connector.py
├── signal_connector.py
├── whatsapp_connector.py
├── homeassistant_connector.py
├── webhook_connector.py         # 汎用 HTTP（スタブ/ベース）
├── templates/
│   ├── connector_template.py    # 新しいコネクターのテンプレート
│   ├── setup_wizard.py          # 対話型 CLI ウィザード
│   ├── telegram_template.yaml
│   ├── whatsapp_template.yaml
│   └── notification_template.yaml
├── LICENSE                      # MIT
├── requirements.txt             # pyyaml（ウィザードのみ）、他は stdlib
├── CHANGELOG.md
├── TODO.md
└── llms.txt
```

## 依存関係

- **コア:** Python 3.8+、標準ライブラリのみ (`urllib`、`json`、`threading`、`subprocess`)
- **セットアップウィザード:** `pyyaml` (`pip install pyyaml`)
- **signal_connector:** `signal-cli` バイナリ — https://github.com/AsamK/signal-cli

## 関連プロジェクト

- **lock-master** (https://github.com/dev-bricks/lock-master) — 関連マルチエージェントコンポーネント
- **ticket-master** (https://github.com/dev-bricks/ticket-master) — 関連マルチエージェントコンポーネント

## 関連モジュール

- **USMC** (`.MODULES/usmc`): エージェント間共有メモリ
- **clutch** (`.MODULES/clutch`): モデルルーティング（エージェントから LLM へ）
- **connectors**（このモジュール）: メッセージング（エージェントから人間へ）
