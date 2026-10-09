from datetime import datetime, timezone

from fastapi import FastAPI

app = FastAPI(
    title="Docker Mastery Demo API",
    description="Advanced Docker demonstration application",
    version="1.2.0",
)


@app.get("/")
def root():
    """Root endpoint - simple welcome message."""
    return {
        "message": "Welcome to the Docker Mastery Demo API",
        "phase": "3 - advanced",
        "status": "running",
    }


@app.get("/health")
def health():
    """Health check endpoint used by the container."""
    """Also used by CI smoke tests."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/info")
def info():
    return {
        "app": "docker-mastery-demo",
        "version": app.version,
        "phase": "3 - advanced",
    }
