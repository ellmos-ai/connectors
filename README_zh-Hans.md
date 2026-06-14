[EN](README.md) | [DE](README_de.md) | [ES](README_es.md) | [JA](README_ja.md) | [RU](README_ru.md) | **ZH**

# connectors

独立的 Python 消息连接器模块，支持 Telegram、Discord、Signal、
WhatsApp、Home Assistant 和通用 HTTP Webhook。

从 [BACH](../../.AI/.OS/BACH/) (`.OS/BACH/system/connectors/`) 中提取并解耦。
无需任何框架。无强制外部依赖（仅使用标准库）。

> **状态：** v1.0.0 — 功能完整，尚未作为独立包发布。
> 计划中的改进请参见 [TODO.md](TODO.md)。

## 支持的连接器

| 连接器          | 协议                  | 来源                       | 状态    |
|-----------------|-----------------------|----------------------------|---------|
| `telegram`      | Telegram Bot API      | 从 BACH 移植               | 稳定    |
| `discord`       | Discord Bot + Webhook | 从 BACH 移植               | 稳定    |
| `signal`        | signal-cli            | 从 BACH 移植               | 稳定    |
| `whatsapp`      | WhatsApp Business API | 从 BACH 移植               | 稳定    |
| `homeassistant` | Home Assistant REST   | 从 BACH 移植               | 稳定    |
| `webhook`       | 通用 HTTP POST        | 新增（BACH 中无对应实现）  | 存根    |

`webhook` 连接器是**新增内容** — 在早期规划文档中有所提及，但在 BACH 中并不存在。
它作为基本的单向 HTTP POST 连接器可正常使用，并明确标记为存根/基础实现。

## 快速开始

```python
import os
from connectors import create_connector, ConnectorConfig

# Telegram 示例
config = ConnectorConfig(
    name="my_bot",
    connector_type="telegram",
    auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]},
    options={"owner_chat_id": ""},   # 可选：仅接受此聊天的消息
)
conn = create_connector(config)
if conn.connect():
    conn.send_message("CHAT_ID", "你好!")

# 接收消息（轮询）
thread, stop = conn.poll_threaded(on_message=lambda m: print(m.content))
# ... 稍后：
stop.set()
```

## 密钥管理

**切勿将 token 硬编码到代码中。** 推荐方式：

```python
# 1. 环境变量（最简单）
auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]}

# 2. python-dotenv
from dotenv import load_dotenv; load_dotenv()
auth_config={"bot_token": os.getenv("TG_BOT_TOKEN")}

# 3. SecretAdapter（框架集成，例如 BACH）
from connectors.base import SecretAdapter

class MyAdapter(SecretAdapter):
    def get_secret(self, key: str) -> str:
        return my_vault.get(key, "")

conn = create_connector(config, secret_adapter=MyAdapter())
```

## 构建自定义连接器

使用交互式向导：

```bash
pip install pyyaml   # 仅向导需要
python -m connectors.templates.setup_wizard
```

或手动使用 `templates/connector_template.py`：

1. 将 `connector_template.py` 复制为 `my_connector.py`
2. 替换所有 `{{PLACEHOLDER}}` 占位符
3. 实现 `connect()`、`disconnect()`、`send_message()`、`get_messages()`
4. 在 `__init__.py` 的 `_CONNECTOR_MAP` 中注册

## BACH 集成（可选）

要在 BACH 内使用本模块，请实现指向 `hub.secrets_handler.SecretsHandler` 的 `SecretAdapter`：

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

BACH 随后可以选择性地将其 `connectors/` 层切换到本模块。
详情请参见 [BACH-REIMPORT-NOTE.md](BACH-REIMPORT-NOTE.md)。

## 项目结构

```
connectors/
├── __init__.py                  # create_connector() 工厂函数
├── base.py                      # BaseConnector, Message, SecretAdapter
├── telegram_connector.py
├── discord_connector.py
├── signal_connector.py
├── whatsapp_connector.py
├── homeassistant_connector.py
├── webhook_connector.py         # 通用 HTTP（存根/基础）
├── templates/
│   ├── connector_template.py    # 新连接器模板
│   ├── setup_wizard.py          # 交互式 CLI 向导
│   ├── telegram_template.yaml
│   ├── whatsapp_template.yaml
│   └── notification_template.yaml
├── LICENSE                      # MIT
├── requirements.txt             # pyyaml（仅向导），其余为标准库
├── CHANGELOG.md
├── TODO.md
└── llms.txt
```

## 依赖关系

- **核心：** Python 3.8+，仅标准库（`urllib`、`json`、`threading`、`subprocess`）
- **设置向导：** `pyyaml`（`pip install pyyaml`）
- **signal_connector：** `signal-cli` 二进制文件 — https://github.com/AsamK/signal-cli

## 相关项目

- **lock-master** (https://github.com/dev-bricks/lock-master) — 相关多智能体组件
- **ticket-master** (https://github.com/dev-bricks/ticket-master) — 相关多智能体组件

## 相关模块

- **USMC** (`.MODULES/usmc`)：智能体间共享内存
- **clutch** (`.MODULES/clutch`)：模型路由（智能体到 LLM）
- **connectors**（本模块）：消息传递（智能体到人类）
