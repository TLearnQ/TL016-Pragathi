import requests

class APIResponseError(Exception):
    """Raised when an HTTP call fails or returns  status."""
    def __init__(self, message, status_code=None, url=None):
        super().__init__(message)
        self.status_code = status_code
        self.url = url

    def to_dict(self):
        return {"message": str(self), "status_code": self.status_code, "url": self.url}

class APIClient:
    def __init__(self, timeout=15, headers=None):
        self.session = requests.Session()
        self.timeout = timeout
        if headers:
            self.session.headers.update(headers)

    def get_text(self, url):
        """
        GET a URL and return text. Raises APIResponseError on network or statuses.
        """
        try:
            resp = self.session.get(url, timeout=self.timeout)
        except requests.RequestException as e:
            raise APIResponseError(f"Network error: {e}", status_code=None, url=url) from e

        if not (200 <= resp.status_code < 300):
            # include truncated body to help debugging
            snippet = resp.text[:400] if resp.text else None
            raise APIResponseError(f"HTTP {resp.status_code} fetching {url}. Body (truncated): {snippet}",
                                   status_code=resp.status_code, url=url)
        return resp.text

