import logging

# Configure logging
logging.basicConfig(
    filename="notifications.log",  # Log notifications to a file
    level=logging.INFO,  # Set logging level
    format="%(asctime)s - %(levelname)s - %(message)s",  # Log format
)

logger = logging.getLogger(__name__)
