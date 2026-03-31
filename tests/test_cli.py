import json
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

import json
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from main import app

runner = CliRunner()


@patch('smtplib.SMTP')
def test_cli_send_email(mock_smtp_class):
    """Test CLI invocation of gmail_send command (dry run with mocked SMTP)."""
    mock_smtp = MagicMock()
    mock_smtp_class.return_value = mock_smtp

    result = runner.invoke(
        app,
        [
            "gmail-send",
            "test@gmail.com",
            "1234567890123456",
            "# Hello\n\nThis is a CLI test",
            "recipient@example.com",
            "--subject",
            "CLI Test",
        ],
    )

    assert result.exit_code == 0
    # Should output valid JSON
    output = result.stdout.strip()
    assert output.startswith('{') and output.endswith('}')
    parsed = json.loads(output)
    assert 'success' in parsed