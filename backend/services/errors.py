class ProviderError(Exception):
    """Upstream provider failure; `provider` names the engine/model/service."""

    def __init__(self, provider: str, message: str, status_code: int = 424, extra: dict | None = None):
        super().__init__(f"{provider}: {message}")
        self.provider = provider
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}


class UnsupportedError(Exception):
    pass
