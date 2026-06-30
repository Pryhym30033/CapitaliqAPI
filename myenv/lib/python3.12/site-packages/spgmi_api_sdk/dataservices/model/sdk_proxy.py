from dataclasses import dataclass, field
from typing import Optional

@dataclass
class SDKProxy:
    proxy_username: Optional[str] = field(default="")
    proxy_password: Optional[str] = field(default="")
    proxy_host: Optional[str] = field(default=None)
    proxy_port: Optional[int] = field(default=None)
    proxy_domain: Optional[str] = field(default="")

    def __str__(self):
        return (f"SDKProxy(proxy_username={self.proxy_username}, proxy_password={self.proxy_password}, "
                f"proxy_host={self.proxy_host}, proxy_port={self.proxy_port}, proxy_domain={self.proxy_domain})")

