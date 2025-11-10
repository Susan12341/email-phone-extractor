from typing import List, Dict
import requests

class APIConnector:
    """
    Sends extracted records to a remote API endpoint in batches.
    """

    def __init__(self, endpoint: str | None, api_key: str | None, timeout: float = 20, logger=None):
        if not endpoint:
            raise ValueError("API endpoint is required when API is enabled.")
        self.endpoint = endpoint
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logger

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def send_batch(self, records: List[Dict], batch_size: int = 500) -> int:
        if not records:
            return 0
        sent_batches = 0
        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            resp = requests.post(
                self.endpoint, json=batch, headers=self._headers(), timeout=self.timeout
            )
            if resp.status_code >= 400:
                msg = f"API error {resp.status_code}: {resp.text[:200]}"
                if self.logger:
                    self.logger.error(msg)
                else:
                    raise RuntimeError(msg)
            else:
                if self.logger:
                    self.logger.debug(f"Batch {sent_batches+1} OK ({len(batch)} items)")
                sent_batches += 1
        return sent_batches