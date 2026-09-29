from typing import Literal

from pydantic import BaseModel, Field


class MCPServer(BaseModel):
    transport: Literal["streamable_http"] = "streamable_http"
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    timeout: float = 30.0
    sse_read_timeout: float = 300.0
    terminate_on_close: bool = True


class AgentMCPServer(BaseModel):
    name: str
