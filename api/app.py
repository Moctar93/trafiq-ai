from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from ml.analyze_url import run_analysis

app = FastAPI(
    title="Trafiq AI API",
    description=(
        "API REST de démonstration pour l'analyse SEO Trafiq AI : "
        "crawler -> 40 features -> Random Forest -> recommandations."
    ),
    version="0.1.0",
)


class AnalyzeRequest(BaseModel):
    url: str = Field(
        ...,
        min_length=4,
        description="URL complète à analyser.",
        examples=["https://www.lemonde.fr/"],
    )
    timeout: int = Field(default=15, ge=1, le=120)


@app.get("/")
def root() -> dict[str, Any]:
    return {
        "service": "Trafiq AI API",
        "version": app.version,
        "status": "online",
        "endpoints": {
            "health": "GET /health",
            "analyze": "POST /analyze",
            "docs": "GET /docs",
        },
    }


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "trafiq-ai"}


@app.post("/analyze")
def analyze(request: AnalyzeRequest) -> dict[str, Any]:
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="L'URL ne peut pas être vide.")
    if not (url.startswith("http://") or url.startswith("https://")):
        raise HTTPException(
            status_code=400,
            detail="L'URL doit commencer par http:// ou https://.",
        )

    try:
        result = run_analysis(url=url, timeout=request.timeout)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Erreur interne pendant l'analyse : {exc}",
        ) from exc

    return result


if __name__ == "__main__":
    import uvicorn

    host = os.getenv("TRAFIQ_API_HOST", "127.0.0.1")
    port = int(os.getenv("TRAFIQ_API_PORT", "8000"))
    uvicorn.run("api.app:app", host=host, port=port, reload=False)
