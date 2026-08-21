# logdock

Uma biblioteca Python reutilizável para **logging estruturado por execução**, com controle de verbosidade, persistência configurável e envio de alertas para canais de comunicação.

## Principais funcionalidades

* Logs estruturados com contexto da aplicação e da execução.
* Identificador único por execução (`execution_id`).
* Controle independente dos níveis de log por destino.
* Exibição de logs no terminal e em ambientes de nuvem.
* Acúmulo dos registros em memória durante a execução.
* Persistência de um único arquivo de log ao final de cada execução.
* Persistência em documentos **JSON (`.json`)** por execução e lote.
* Resumo final com:

  * status;
  * duração;
  * quantidade de eventos;
  * quantidade de erros.
* Integrações desacopladas por meio de interfaces e adaptadores.
* Persistência pronta para **Azure Blob Storage**.
* Notificações e envio de arquivos para canais de comunicação.
* Integração pronta com **Telegram**.
* Suporte a implementações personalizadas, como:

  * Amazon S3;
  * Slack;
  * e-mail;
  * bancos de dados.
* Isolamento seguro entre execuções concorrentes.
* Tentativa de persistência mesmo quando a execução termina com erro.
* Configuração específica para reduzir logs de bibliotecas externas.
* Proteção para evitar que falhas nos adaptadores ocultem o erro original da aplicação.

## Níveis independentes por destino

Cada destino pode possuir seu próprio nível mínimo de log:

```env
LOG_CONSOLE_LEVEL=INFO
LOG_STORAGE_LEVEL=DEBUG
LOG_NOTIFICATION_LEVEL=ERROR
```

Isso permite:

* manter o terminal mais limpo em produção;
* preservar informações detalhadas no armazenamento;
* enviar somente erros relevantes para o canal de comunicação.

## Inicialização do projeto

Depois de instalar a biblioteca, inicialize o LogDock na raiz da aplicação:

```bash
logdock init
```

O comando cria:

* `logdock.json`, com configurações seguras e integrações desabilitadas;
* `.env.example`, com todas as variáveis aceitas pela biblioteca;
* `local.settings.json.example`, com as mesmas variáveis no formato do Azure Functions.
* `.gitignore`, criado ou atualizado com a regra `logs/`.

Por padrão, o nome da pasta atual vira o `app_name`. Ele pode ser informado com
`logdock init --app-name minha-aplicacao`. Arquivos existentes não são sobrescritos;
nos arquivos de exemplo, somente variáveis ausentes são acrescentadas. Use
`--force` quando quiser recriar os três arquivos do zero.

Para desenvolvimento local, copie apenas o modelo adequado ao ambiente e preencha
as credenciais sem versioná-las:

```bash
cp .env.example .env
cp local.settings.json.example local.settings.json
```

## Variáveis de ambiente

O `logdock.json` contém apenas configurações não sensíveis. Credenciais e dados das
integrações devem ser fornecidos por variáveis de ambiente:

```env
LOGDOCK_TELEGRAM_BOT_TOKEN=
LOGDOCK_TELEGRAM_CHAT_ID=
LOGDOCK_AZURE_FUNCTION_ENDPOINT=
LOGDOCK_AZURE_FUNCTION_KEY=
LOGDOCK_AZURE_BLOB_CONNECTION_STRING=
LOGDOCK_AZURE_BLOB_CONTAINER=
```

As variáveis de um provider são obrigatórias somente quando ele está habilitado no
`logdock.json`. Em Azure Functions, os Application Settings e os valores definidos
em `local.settings.json` durante o desenvolvimento são expostos ao processo como
variáveis de ambiente.

## Persistência manual

O LogDock nunca persiste registros automaticamente. Quando a persistência está
habilitada, os logs da execução ficam em memória até que `persist()` seja chamado:

```python
logdock = LogDock()

try:
    logdock.info("Processamento iniciado")
    executar_processo()
    result = logdock.persist()
except Exception as error:
    logdock.error(f"Falha no processamento: {error}")
    result = logdock.persist()
    raise
```

O provider local é o padrão e grava documentos JSON identificados pela execução:

```json
{
  "persistence": {
    "enabled": true,
    "provider": "LOCAL",
    "path": "./logs"
  }
}
```

Cada documento possui um bloco `execution`, com o identificador curto e os metadados
do lote, e um array `logs`. Os registros respeitam as opções de `format`: horário e
origem são incluídos somente quando habilitados; a precisão do horário e o uso do
caminho completo da origem também seguem o `logdock.json`. O nome da aplicação,
quando habilitado, aparece uma única vez nos metadados da execução.

Para persistir no Azure Blob Storage, use `"provider": "AZURE_BLOB_STORAGE"` e
configure `LOGDOCK_AZURE_BLOB_CONNECTION_STRING` e
`LOGDOCK_AZURE_BLOB_CONTAINER`. Em caso de sucesso, o buffer persistido é limpo;
em caso de falha, ele é preservado para uma nova tentativa.

## Formatação do horário

O horário do log pode ser habilitado e personalizado no `logdock.json`:

```json
{
  "format": {
    "time": {
      "enabled": true,
      "timezone": "America/Sao_Paulo",
      "precision": "SECOND"
    }
  }
}
```

As precisões suportadas são `DAY`, `HOUR`, `MINUTE`, `SECOND` e `MILLISECOND`.
O fuso deve usar um identificador IANA, como `UTC`, `America/Sao_Paulo` ou
`Europe/Lisbon`. Se `format` não estiver presente, o horário fica desabilitado.

## Nome da aplicação e origem

O nome da aplicação e o arquivo que originou o log também podem ser configurados:

```json
{
  "format": {
    "app_name": {
      "enabled": true
    },
    "source": {
      "enabled": true,
      "full_path": false
    }
  }
}
```

Com `full_path` igual a `false`, somente o nome do arquivo é exibido. Com `true`,
é exibido seu caminho absoluto. Por padrão, tanto `app_name` quanto `source` ficam
desabilitados.
