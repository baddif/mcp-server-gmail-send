# Gmail Send Skill

This document defines the input/output contract and usage examples for the `gmail_send` skill.

## Input Schema (JSON Schema)

```json
{
  "type": "object",
  "properties": {
    "username": { "type": "string", "description": "Gmail username (email address)" },
    "app_password": { "type": "string", "description": "16-character Gmail App Password" },
    "content": { "type": "string", "description": "Email content in Markdown format" },
    "to_email": { "type": "string", "description": "Recipient email address" },
    "subject": { "type": "string", "description": "Email subject line", "default": "Email from Gmail Send Skill" },
    "from_name": { "type": "string", "description": "Display name for the sender", "default": null }
  },
  "required": ["username", "app_password", "content", "to_email"]
}
```

## Output Schema

All outputs MUST follow the core contract:

Success:

```json
{
  "success": true,
  "data": { /* result object */ },
  "error": null
}
```

Failure:

```json
{
  "success": false,
  "data": null,
  "error": "Error message"
}
```

## CLI Example

```bash
python3 main.py gmail-send \ 
  "sender@gmail.com" "abcd efgh ijkl mnop" "# Hello\n\nThis is a test" "recipient@example.com" --subject "Test"
```

CLI output MUST be valid JSON and contain no additional logging on stdout.

## MCP Example

Request: MCP tool invocation `gmail_send` with parameters as above.

Response: MCP transport MUST return the content wrapper containing a JSON string with the output schema.

## Notes

- Never include credentials in repository files.
- Use App Passwords and enable 2FA.
