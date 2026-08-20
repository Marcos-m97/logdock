import argparse
import json
from pathlib import Path


ENV_DEFAULTS = {
    "LOGDOCK_TELEGRAM_BOT_TOKEN": "",
    "LOGDOCK_TELEGRAM_CHAT_ID": "",
    "LOGDOCK_AZURE_FUNCTION_ENDPOINT": "",
    "LOGDOCK_AZURE_FUNCTION_KEY": "",
    "LOGDOCK_AZURE_BLOB_CONNECTION_STRING": "",
    "LOGDOCK_AZURE_BLOB_CONTAINER": "",
}


def _default_config(app_name: str) -> dict:
    return {
        "app_name": app_name,
        "log_level": "INFO",
        "notification": {"enabled": False, "provider": ""},
        "persistence": {"enabled": False, "provider": ""},
        "format": {
            "time_enabled": True,
            "timezone": "UTC",
            "time_precision": "SECOND",
            "app_name_enabled": True,
            "source_enabled": True,
            "source_full_path": False,
        },
    }


def _write_json(path: Path, content: dict, force: bool) -> str:
    existed = path.exists()
    if existed and not force:
        return "mantido"
    path.write_text(
        json.dumps(content, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return "sobrescrito" if existed else "criado"


def _update_env_example(path: Path, force: bool) -> str:
    if force or not path.exists():
        existed = path.exists()
        content = "\n".join(f"{name}={value}" for name, value in ENV_DEFAULTS.items())
        path.write_text(content + "\n", encoding="utf-8")
        return "sobrescrito" if existed else "criado"

    content = path.read_text(encoding="utf-8")
    configured_names = {
        line.split("=", 1)[0].strip()
        for line in content.splitlines()
        if "=" in line and not line.lstrip().startswith("#")
    }
    missing = [name for name in ENV_DEFAULTS if name not in configured_names]
    if not missing:
        return "mantido"

    separator = "" if not content or content.endswith("\n") else "\n"
    addition = "\n".join(f"{name}={ENV_DEFAULTS[name]}" for name in missing)
    path.write_text(content + separator + addition + "\n", encoding="utf-8")
    return f"atualizado ({len(missing)} variável(is) adicionada(s))"


def _update_local_settings_example(path: Path, force: bool) -> str:
    base = {
        "IsEncrypted": False,
        "Values": {
            "AzureWebJobsStorage": "",
            "FUNCTIONS_WORKER_RUNTIME": "python",
            **ENV_DEFAULTS,
        },
    }
    if force or not path.exists():
        existed = path.exists()
        path.write_text(
            json.dumps(base, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        return "sobrescrito" if existed else "criado"

    try:
        current = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as error:
        raise ValueError(f"Não foi possível atualizar {path}: {error}") from error

    values = current.setdefault("Values", {})
    if not isinstance(values, dict):
        raise ValueError(f"A propriedade 'Values' de {path} deve ser um objeto JSON.")
    missing = {name: value for name, value in ENV_DEFAULTS.items() if name not in values}
    if not missing:
        return "mantido"
    values.update(missing)
    path.write_text(
        json.dumps(current, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return f"atualizado ({len(missing)} variável(is) adicionada(s))"


def init_project(
    directory: Path, app_name: str | None = None, force: bool = False
) -> list[tuple[Path, str]]:
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=True)
    resolved_app_name = app_name or directory.name

    return [
        (directory / ".env.example", _update_env_example(directory / ".env.example", force)),
        (
            directory / "local.settings.json.example",
            _update_local_settings_example(directory / "local.settings.json.example", force),
        ),
        (
            directory / "logdock.json",
            _write_json(directory / "logdock.json", _default_config(resolved_app_name), force),
        ),
    ]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="logdock")
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="cria os arquivos iniciais do LogDock")
    init_parser.add_argument("--app-name", help="nome da aplicação (padrão: nome da pasta)")
    init_parser.add_argument(
        "--directory",
        type=Path,
        default=Path.cwd(),
        help="diretório do projeto (padrão: diretório atual)",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="sobrescreve os três arquivos com os valores padrão",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        results = init_project(args.directory, args.app_name, args.force)
    except (OSError, ValueError) as error:
        print(f"Erro: {error}")
        return 1
    for path, status in results:
        print(f"{status.capitalize()}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
