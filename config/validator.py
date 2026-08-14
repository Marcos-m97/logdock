from .suported import (
    SUPORTED_LEVELS,
    SUPORTED_NOTIFICATION_PROVIDERS,
    SUPORTED_PERSISTENCE_PROVIDERS,
)

class InvalidSettingsException(Exception):
    pass

def validate_suported(
    level_name,
    notification_provider,
    persistence_provider,
):
    if notification_provider != "" and notification_provider not in SUPORTED_NOTIFICATION_PROVIDERS:
        raise InvalidSettingsException(
            f"Notification provider inválido: '{notification_provider}'. "
            f"Valores suportados: {SUPORTED_NOTIFICATION_PROVIDERS}"
        )

    if persistence_provider != "" and persistence_provider not in SUPORTED_PERSISTENCE_PROVIDERS:
        raise InvalidSettingsException(
            f"Persistence provider inválido: '{persistence_provider}'. "
            f"Valores suportados: {SUPORTED_PERSISTENCE_PROVIDERS}"
        )

    if level_name not in SUPORTED_LEVELS:
        raise InvalidSettingsException(
            f"Level inválido: '{level_name}'. "
            f"Valores suportados: {SUPORTED_LEVELS}"
        )