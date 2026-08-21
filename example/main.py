import sys
from pathlib import Path

# Permite executar este arquivo diretamente py example\main.py a partir da raiz da lib
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# from core.logdock import LogDock 
from logdock import LogDock

from dotenv import load_dotenv

load_dotenv()

logdock = LogDock()

logdock.info("teste info")

# logdock.error("teste erro")

logdock.error("teste erro com notificação", notify=True)

logdock.debug("teste debug")

logdock.warning("teste warning")

# A persistência nunca ocorre automaticamente. Quando habilitada no
# logdock.json, o desenvolvedor decide explicitamente quando chamá-la.
result = logdock.persist()
if not result.success:
    logdock.warning(f"Logs não persistidos: {result.error}")
