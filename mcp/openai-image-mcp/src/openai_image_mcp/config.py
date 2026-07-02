import os
import sys
from dataclasses import dataclass, field

ENV_PREFIX = "OPENAI_IMAGE_MCP_"

KNOWN_FIELDS = frozenset({
    "API",
    "KEY",
    "MODEL",
    "ASYNC",
    "TIMEOUT",
    "TIMEOUT_POLL",
    "TIMEOUT_MAX_WAIT",
    "TOOL_NAME",
    "TOOL_DESCRIPTION",
})

REQUIRED_FIELDS = ("API", "KEY", "MODEL")


@dataclass
class TimeoutConfig:
    timeout: int = 120
    poll_interval: int = 5
    max_wait: int = 600


@dataclass
class ToolConfig:
    name: str | None = None
    description: str = ""


@dataclass
class BackendConfig:
    base_url: str
    api_key: str
    async_mode: bool
    models: list[str] = field(default_factory=list)
    timeout: TimeoutConfig = field(default_factory=TimeoutConfig)
    tool: ToolConfig = field(default_factory=ToolConfig)


def _scan_env() -> dict[str, dict[str, str]]:
    """Scan environment for ``OPENAI_IMAGE_MCP_<SERVICE>_<FIELD>`` entries.

    Service name must be ``[A-Z0-9]+`` (alnum only, no underscores or hyphens)
    so it can be unambiguously split from the field suffix.

    Returns a dict mapping service name (lowercase) to a dict of field -> value.
    """
    services: dict[str, dict[str, str]] = {}
    sorted_fields = sorted(KNOWN_FIELDS, key=len, reverse=True)

    for env_key, env_val in os.environ.items():
        if not env_key.startswith(ENV_PREFIX):
            continue
        rest = env_key[len(ENV_PREFIX):]

        matched_field: str | None = None
        matched_service: str | None = None
        for field_name in sorted_fields:
            suffix = "_" + field_name
            if rest.endswith(suffix):
                service_part = rest[:-len(suffix)]
                if service_part and service_part.isalnum():
                    matched_field = field_name
                    matched_service = service_part
                    break

        if matched_field is None:
            continue

        name = matched_service.lower()
        services.setdefault(name, {})[matched_field] = env_val

    return services


def load_backends() -> dict[str, BackendConfig]:
    services = _scan_env()

    if not services:
        sys.exit(
            "No services configured. Set environment variables like "
            "OPENAI_IMAGE_MCP_<SERVICE>_<FIELD> (required fields: "
            "API, KEY, MODEL). Example: "
            "OPENAI_IMAGE_MCP_SENSENOVA_API=https://... "
            "OPENAI_IMAGE_MCP_SENSENOVA_KEY=sk-... "
            "OPENAI_IMAGE_MCP_SENSENOVA_MODEL=sensenova-u1-fast"
        )

    backends: dict[str, BackendConfig] = {}
    for name, fields in services.items():
        for required in REQUIRED_FIELDS:
            if required not in fields:
                sys.exit(
                    f"Service '{name}' missing OPENAI_IMAGE_MCP_"
                    f"{name.upper()}_{required}"
                )

        try:
            timeout = TimeoutConfig(
                timeout=int(fields.get("TIMEOUT", 120)),
                poll_interval=int(fields.get("TIMEOUT_POLL", 5)),
                max_wait=int(fields.get("TIMEOUT_MAX_WAIT", 600)),
            )
        except ValueError as exc:
            sys.exit(f"Service '{name}' invalid timeout value: {exc}")

        tool = ToolConfig(
            name=fields.get("TOOL_NAME"),
            description=fields.get("TOOL_DESCRIPTION", ""),
        )

        models = [m.strip() for m in fields["MODEL"].split(",") if m.strip()]
        if not models:
            sys.exit(f"Service '{name}' has empty MODEL list")

        backends[name] = BackendConfig(
            base_url=fields["API"],
            api_key=fields["KEY"],
            async_mode=fields.get("ASYNC", "false").lower() == "true",
            models=models,
            timeout=timeout,
            tool=tool,
        )

    return backends
