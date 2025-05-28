import logging
from flask_migrate import upgrade
from web import app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def on_starting(server):
    with app.app_context():
        upgrade()
        logger.info(
            "Database migrations applied successfully. Scheduler job activated for user data processing."
        )
