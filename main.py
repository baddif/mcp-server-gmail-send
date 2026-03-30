import sys
import json
import asyncio
import typer
from typing import Optional

from mcp.server.fastmcp import FastMCP
from gmail_send_skill import GmailSendSkill

app = typer.Typer()
mcp = FastMCP("Gmail Send")
impl = GmailSendSkill()

_is_cli = len(sys.argv) > 1

def format_mcp(result: dict):
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, ensure_ascii=False)
            }
        ]
    }


@mcp.tool()
@app.command()
def gmail_send(
    username: str = typer.Argument(..., help="Gmail username (email address)"),
    app_password: str = typer.Argument(..., help="16-character Gmail App Password"),
    content: str = typer.Argument(..., help="Email content in Markdown format"),
    to_email: str = typer.Argument(..., help="Recipient email address"),
    subject: Optional[str] = typer.Option("Email from Gmail Send Skill", help="Email subject line"),
    from_name: Optional[str] = typer.Option(None, help="Display name for the sender")
):
    """Send email via Gmail using App Password authentication"""
    try:
        if asyncio.iscoroutinefunction(impl.execute):
            result = asyncio.run(impl.execute(
                username=username,
                app_password=app_password,
                content=content,
                to_email=to_email,
                subject=subject,
                from_name=from_name
            ))
        else:
            result = impl.execute(
                impl=impl,
                ctx=None,
                username=username,
                app_password=app_password,
                content=content,
                to_email=to_email,
                subject=subject,
                from_name=from_name
            )

        if _is_cli:
            typer.echo(json.dumps(result, ensure_ascii=False))
        else:
            return json.dumps(result, ensure_ascii=False)

    except Exception as e:
        error = {
            "success": False,
            "data": None,
            "error": str(e)
        }
        if _is_cli:
            typer.echo(json.dumps(error), err=True)
            raise typer.Exit(1)
        else:
            return json.dumps(error)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        app()
    else:
        # Run MCP server transport
        mcp.run(transport="stdio")
