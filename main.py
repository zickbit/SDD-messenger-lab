import os

import uvicorn

from app.api.main import create_app


app = create_app()


if __name__ == "__main__":
    host = os.environ.get("MESSENGER_HOST", "127.0.0.1")
    port = int(os.environ.get("MESSENGER_PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
