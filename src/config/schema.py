from __future__ import annotations
from pydantic import BaseModel, Field


class EndpointCfg(BaseModel):
base_url: str
readiness: str = "/readiness"
liveness: str = "/liveness"


class ThresholdsCfg(BaseModel):
http_latency_ms: int = 300
coverage_min: float = 0.8


class PathsCfg(BaseModel):
repo: str = "."


class AuditConfig(BaseModel):
endpoints: EndpointCfg
thresholds: ThresholdsCfg = Field(default_factory=ThresholdsCfg)
paths: PathsCfg = Field(default_factory=PathsCfg)