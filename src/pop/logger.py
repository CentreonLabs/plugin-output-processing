import logging
import uvicorn

logger = logging.getLogger("pop")

logger.setLevel(logging.INFO)

formatter = uvicorn.logging.DefaultFormatter(
    "%(asctime)s | %(levelprefix)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

handler.setFormatter(formatter)

logger.addHandler(handler)
