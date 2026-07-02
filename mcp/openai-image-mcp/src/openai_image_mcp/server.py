from logging import INFO, basicConfig, getLogger
from pathlib import Path

from fastmcp import FastMCP
from pydantic import Field

from .client import generate
from .config import BackendConfig, load_backends

basicConfig(level=INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = getLogger(__name__)

backends = load_backends()
mcp = FastMCP(name="OpenAI Image Gen MCP")


@mcp.tool
def list_models() -> str:
    """List all configured image generation tools (one per backend) and their supported models."""
    lines = []
    for backend_name, cfg in backends.items():
        tool_name = cfg.tool.name or f"{backend_name}_generate_image"
        lines.append(f"## {tool_name}")
        for model_id in cfg.models:
            async_label = " [async]" if cfg.async_mode else ""
            lines.append(f"  - `{model_id}`{async_label}")
    return "\n".join(lines)


def _make_tool(backend_name: str, cfg: BackendConfig):
    """Build an MCP tool function bound to a single backend's config."""

    def generate_image(
        model: str = Field(
            description=f"Model ID. Available for this backend: {', '.join(cfg.models)}",
        ),
        prompt: str = Field(description="Image description text"),
        size: str | None = Field(
            default=None,
            description="Image size WxH (backend-dependent; omit for default)",
        ),
        n: int = Field(default=1, ge=1, le=4, description="Number of images to generate (1-4)"),
        image: str | None = Field(
            default=None,
            description="Reference image URL / data URI / local file path",
        ),
        save_path: str | None = Field(
            default=None,
            description=(
                "Optional local file path. If provided, the first generated image is "
                "downloaded and saved here. Returns 'Saved: <path>' plus the URL."
            ),
        ),
    ) -> str:
        if model not in cfg.models:
            return f"Error: model '{model}' not found. Available: {cfg.models}"

        logger.info(
            "generate_image: backend=%s model=%s size=%s n=%d image=%s save_path=%s",
            backend_name, model, size, n, image is not None, save_path,
        )
        try:
            results = generate(cfg, model, prompt, size, n, image)
        except Exception as exc:
            logger.exception("generate_image failed")
            return f"Error: {type(exc).__name__}: {exc}"

        urls = [r.url for r in results if r.url]

        if save_path and results:
            first = results[0]
            try:
                content = first.to_bytes()
                path = Path(save_path)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(content)
                source = "b64_json" if first.b64_json else "url"
                msg = f"Saved: {path.resolve()}\nSource: {source}"
                if first.url:
                    msg += f"\nURL: {first.url}"
                return msg
            except Exception as exc:
                logger.exception("save_path failed")
                source = "b64_json" if first.b64_json else "url"
                url_line = f"\nURL: {first.url}" if first.url else ""
                return (
                    f"Error: failed to save to '{save_path}': "
                    f"{type(exc).__name__}: {exc}\n"
                    f"Source: {source}{url_line}"
                )

        return "\n".join(urls)

    return generate_image


for backend_name, cfg in backends.items():
    fn = _make_tool(backend_name, cfg)
    tool_name = cfg.tool.name or f"{backend_name}_generate_image"
    description = cfg.tool.description or f"Generate images via {backend_name} backend"
    mcp.tool(name=tool_name, description=description)(fn)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
