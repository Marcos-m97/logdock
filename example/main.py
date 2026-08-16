import sys
from pathlib import Path

# Permite executar este arquivo diretamente com `py main.py` dentro de example/.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.logdock_core import LogDock 

logdock = LogDock()

logdock.info("teste info")

logdock.error("teste erro")

logdock.error("teste erro com notificação", notify=True)

logdock.debug("teste debug")

logdock.warning("teste warning")