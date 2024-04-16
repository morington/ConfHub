from dataclasses import dataclass, asdict
from typing import get_type_hints, Optional

import yarl

from confhub.exceptions import ModelConfigError


@dataclass
class URLConfig:
    scheme: str
    port: int
    host: str = '127.0.0.1'
    path: str = '/'
    user: Optional[str] = None
    password: Optional[str] = None

    def __post_init__(self) -> None:
        type_hints = get_type_hints(URLConfig)

        for field_name, type_ in type_hints.items():
            value = getattr(self, field_name)
            if not isinstance(value, type_):
                print(type(type_))
                raise ModelConfigError(item=field_name, item_type=type_)

    def __repr__(self) -> str:
        return f"<ServiceConfig URL::{self.host}:{self.port}@{self.user}:{self.password}/{self.path}>"

    def __str__(self) -> str:
        return f"<ServiceConfig URL::{self.host}:{self.port}@{'*' * len(self.user)}:{'*' * len(self.password)}/{self.path}>"

    def get_human_url(self) -> str:
        url = yarl.URL.build(**asdict(self))

        return url.human_repr()
