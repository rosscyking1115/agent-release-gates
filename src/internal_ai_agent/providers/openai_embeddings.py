from __future__ import annotations

import json
import os
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any
from urllib import request

DEFAULT_OPENAI_EMBEDDING_ENDPOINT = "https://api.openai.com/v1/embeddings"
DEFAULT_OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
DEFAULT_OPENAI_EMBEDDING_BATCH_SIZE = 64

HttpPost = Callable[[str, bytes, Mapping[str, str], float], str]


@dataclass(frozen=True)
class OpenAIEmbeddingConfig:
    api_key: str
    model: str = DEFAULT_OPENAI_EMBEDDING_MODEL
    endpoint: str = DEFAULT_OPENAI_EMBEDDING_ENDPOINT
    batch_size: int = DEFAULT_OPENAI_EMBEDDING_BATCH_SIZE
    dimensions: int | None = None
    timeout_seconds: float = 30.0


class OpenAIEmbeddingClient:
    def __init__(
        self,
        config: OpenAIEmbeddingConfig,
        *,
        http_post: HttpPost | None = None,
    ) -> None:
        if not config.api_key:
            raise ValueError("api_key is required")
        if config.batch_size < 1:
            raise ValueError("batch_size must be at least 1")
        self.config = config
        self._http_post = http_post or _http_post

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        if any(not text.strip() for text in texts):
            raise ValueError("embedding inputs must be non-empty strings")

        embeddings: list[list[float]] = []
        for index in range(0, len(texts), self.config.batch_size):
            batch = texts[index : index + self.config.batch_size]
            embeddings.extend(self._embed_batch(batch))
        return embeddings

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        payload: dict[str, Any] = {
            "model": self.config.model,
            "input": texts,
            "encoding_format": "float",
        }
        if self.config.dimensions is not None:
            payload["dimensions"] = self.config.dimensions

        response_text = self._http_post(
            self.config.endpoint,
            json.dumps(payload).encode("utf-8"),
            {
                "Authorization": f"Bearer {self.config.api_key}",
                "Content-Type": "application/json",
            },
            self.config.timeout_seconds,
        )
        response = json.loads(response_text)
        data = sorted(response.get("data", []), key=lambda item: int(item["index"]))
        embeddings = [[float(value) for value in item["embedding"]] for item in data]
        if len(embeddings) != len(texts):
            raise ValueError("provider returned a different embedding count than requested")
        return embeddings


def openai_embedding_config_from_env(
    env: Mapping[str, str] | None = None,
) -> OpenAIEmbeddingConfig | None:
    values = env or os.environ
    api_key = values.get("OPENAI_API_KEY", "")
    if not api_key:
        return None

    dimensions = values.get("OPENAI_EMBEDDING_DIMENSIONS")
    return OpenAIEmbeddingConfig(
        api_key=api_key,
        model=values.get("OPENAI_EMBEDDING_MODEL", DEFAULT_OPENAI_EMBEDDING_MODEL),
        endpoint=values.get("OPENAI_EMBEDDING_ENDPOINT", DEFAULT_OPENAI_EMBEDDING_ENDPOINT),
        batch_size=int(
            values.get("OPENAI_EMBEDDING_BATCH_SIZE", DEFAULT_OPENAI_EMBEDDING_BATCH_SIZE)
        ),
        dimensions=int(dimensions) if dimensions else None,
        timeout_seconds=float(values.get("OPENAI_EMBEDDING_TIMEOUT_SECONDS", "30")),
    )


def _http_post(
    endpoint: str,
    body: bytes,
    headers: Mapping[str, str],
    timeout_seconds: float,
) -> str:
    http_request = request.Request(
        endpoint,
        data=body,
        headers=dict(headers),
        method="POST",
    )
    with request.urlopen(http_request, timeout=timeout_seconds) as response:
        return response.read().decode("utf-8", errors="replace")
