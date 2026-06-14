[ES] | [EN](README.md) | [DE](README_de.md) | **ES** | [JA](README_ja.md) | [RU](README_ru.md) | [ZH](README_zh-Hans.md)

# connectors

Módulo Python independiente para conectores de mensajería: Telegram, Discord, Signal,
WhatsApp, Home Assistant y webhooks HTTP genéricos.

Extraído y desacoplado de [BACH](../../.AI/.OS/BACH/) (`.OS/BACH/system/connectors/`).
No requiere ningún framework. Sin dependencias externas obligatorias (solo stdlib).

> **Estado:** v1.0.0 — funcional, aún no publicado como paquete independiente.
> Consulte [TODO.md](TODO.md) para mejoras planificadas.

## Conectores compatibles

| Conector        | Protocolo             | Origen                     | Estado  |
|-----------------|-----------------------|----------------------------|---------|
| `telegram`      | Telegram Bot API      | Portado desde BACH         | Estable |
| `discord`       | Discord Bot + Webhook | Portado desde BACH         | Estable |
| `signal`        | signal-cli            | Portado desde BACH         | Estable |
| `whatsapp`      | WhatsApp Business API | Portado desde BACH         | Estable |
| `homeassistant` | Home Assistant REST   | Portado desde BACH         | Estable |
| `webhook`       | HTTP POST genérico    | Nuevo (sin equivalente BACH)| Stub   |

El conector `webhook` es una **incorporación nueva** — se mencionó en documentos de
planificación anteriores pero no existía en BACH. Es funcional como conector básico
de salida HTTP POST y está claramente marcado como stub/base.

## Inicio rápido

```python
import os
from connectors import create_connector, ConnectorConfig

# Ejemplo Telegram
config = ConnectorConfig(
    name="my_bot",
    connector_type="telegram",
    auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]},
    options={"owner_chat_id": ""},   # opcional: solo aceptar mensajes de este chat
)
conn = create_connector(config)
if conn.connect():
    conn.send_message("CHAT_ID", "Hola!")

# Recibir mensajes (polling)
thread, stop = conn.poll_threaded(on_message=lambda m: print(m.content))
# ... más tarde:
stop.set()
```

## Secretos

**Nunca codifique tokens directamente.** Enfoques recomendados:

```python
# 1. Variables de entorno (más simple)
auth_config={"bot_token": os.environ["TG_BOT_TOKEN"]}

# 2. python-dotenv
from dotenv import load_dotenv; load_dotenv()
auth_config={"bot_token": os.getenv("TG_BOT_TOKEN")}

# 3. SecretAdapter (integración con framework, p. ej. BACH)
from connectors.base import SecretAdapter

class MiAdapter(SecretAdapter):
    def get_secret(self, key: str) -> str:
        return mi_vault.get(key, "")

conn = create_connector(config, secret_adapter=MiAdapter())
```

## Crear un conector personalizado

Use el asistente interactivo:

```bash
pip install pyyaml   # solo necesario para el asistente
python -m connectors.templates.setup_wizard
```

O manualmente, usando `templates/connector_template.py`:

1. Copie `connector_template.py` a `mi_conector.py`
2. Reemplace todos los marcadores `{{PLACEHOLDER}}`
3. Implemente `connect()`, `disconnect()`, `send_message()`, `get_messages()`
4. Registre en `__init__.py` en `_CONNECTOR_MAP`

## Integración con BACH (opcional)

Para usar este módulo dentro de BACH, implemente `SecretAdapter` apuntando a
`hub.secrets_handler.SecretsHandler`:

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

BACH puede entonces cambiar opcionalmente su capa `connectors/` a este módulo.
Consulte [BACH-REIMPORT-NOTE.md](BACH-REIMPORT-NOTE.md) para la nota de tarea correspondiente.

## Estructura del proyecto

```
connectors/
├── __init__.py                  # Fábrica create_connector()
├── base.py                      # BaseConnector, Message, SecretAdapter
├── telegram_connector.py
├── discord_connector.py
├── signal_connector.py
├── whatsapp_connector.py
├── homeassistant_connector.py
├── webhook_connector.py         # HTTP genérico (stub/base)
├── templates/
│   ├── connector_template.py    # Plantilla para nuevos conectores
│   ├── setup_wizard.py          # Asistente CLI interactivo
│   ├── telegram_template.yaml
│   ├── whatsapp_template.yaml
│   └── notification_template.yaml
├── LICENSE                      # MIT
├── requirements.txt             # pyyaml (solo asistente), demás stdlib
├── CHANGELOG.md
├── TODO.md
└── llms.txt
```

## Dependencias

- **Núcleo:** Python 3.8+, solo stdlib (`urllib`, `json`, `threading`, `subprocess`)
- **Asistente de configuración:** `pyyaml` (`pip install pyyaml`)
- **signal_connector:** binario `signal-cli` — https://github.com/AsamK/signal-cli

## Proyectos relacionados

- **lock-master** (https://github.com/dev-bricks/lock-master) — componente multiagente relacionado
- **ticket-master** (https://github.com/dev-bricks/ticket-master) — componente multiagente relacionado

## Módulos relacionados

- **USMC** (`.MODULES/usmc`): Memoria compartida entre agentes
- **clutch** (`.MODULES/clutch`): Enrutamiento de modelos (Agente a LLM)
- **connectors** (este módulo): Mensajería (Agente a humano)
