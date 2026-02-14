"""
Version Management for Gmail Send Skill

Provides version information and management utilities for the Gmail Send Skill MCP server.
"""

import json
from datetime import datetime
from typing import Dict, Any

# Version information
__version__ = "1.0.0"
__release_date__ = "2026-02-14"
__author__ = "AI Assistant"
__description__ = "Gmail Send Skill - Email sending via Gmail with App Password authentication"

# Version metadata
VERSION_INFO = {
    "version": __version__,
    "release_date": __release_date__, 
    "author": __author__,
    "description": __description__,
    "features": [
        "Gmail SMTP email sending",
        "App Password authentication",
        "Markdown to HTML conversion", 
        "MCP (Model Context Protocol) support",
        "OpenAI Function Calling compatibility",
        "Rich error reporting",
        "Email validation"
    ],
    "requirements": [
        "Python 3.7+",
        "smtplib (built-in)",
        "email (built-in)", 
        "markdown (optional, for rich formatting)"
    ],
    "changelog": {
        "1.0.0": {
            "date": "2026-02-14",
            "changes": [
                "Initial release",
                "Gmail send functionality with App Password",
                "Markdown content support",
                "MCP server implementation", 
                "Comprehensive error handling",
                "Email format validation"
            ]
        }
    }
}

def get_version() -> str:
    """Get the version string"""
    return __version__

def get_version_string() -> str:
    """Get descriptive version string"""
    return f"Gmail Send Skill v{__version__} ({__release_date__})"

def get_version_info() -> Dict[str, Any]:
    """Get complete version information"""
    return VERSION_INFO.copy()

def get_changelog(version: str = None) -> Dict[str, Any]:
    """Get changelog for specific version or all versions"""
    if version:
        return VERSION_INFO["changelog"].get(version, {})
    return VERSION_INFO["changelog"]

def get_latest_changes() -> Dict[str, Any]:
    """Get changes for the current version"""
    return get_changelog(__version__)

def print_version_info():
    """Print formatted version information"""
    print(f"Gmail Send Skill")
    print(f"Version: {__version__}")
    print(f"Release Date: {__release_date__}")
    print(f"Author: {__author__}")
    print(f"Description: {__description__}")
    print()
    print("Features:")
    for feature in VERSION_INFO["features"]:
        print(f"  • {feature}")
    print()
    print("Requirements:")
    for req in VERSION_INFO["requirements"]:
        print(f"  • {req}")

def check_updates():
    """Check for potential updates (placeholder for future implementation)"""
    print(f"Current version: {__version__}")
    print("Update checking not implemented yet.")
    print("Please check the repository for newer versions.")

def export_version_info(filepath: str = "version_info.json"):
    """Export version information to JSON file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(VERSION_INFO, f, ensure_ascii=False, indent=2)
        print(f"Version information exported to {filepath}")
    except Exception as e:
        print(f"Failed to export version info: {str(e)}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--info":
            print_version_info()
        elif command == "--version":
            print(__version__)
        elif command == "--check-updates":
            check_updates()
        elif command == "--export":
            filepath = sys.argv[2] if len(sys.argv) > 2 else "version_info.json"
            export_version_info(filepath)
        elif command == "--changelog":
            version = sys.argv[2] if len(sys.argv) > 2 else None
            changelog = get_changelog(version)
            if version and version in changelog:
                print(f"Changelog for v{version}:")
                changes = changelog[version]
                print(f"Date: {changes['date']}")
                print("Changes:")
                for change in changes['changes']:
                    print(f"  • {change}")
            else:
                print("Full Changelog:")
                for ver, details in changelog.items():
                    print(f"\nv{ver} ({details['date']}):")
                    for change in details['changes']:
                        print(f"  • {change}")
        else:
            print("Unknown command. Available commands:")
            print("  --info        Show detailed version information")
            print("  --version     Show version number only")
            print("  --check-updates  Check for updates")
            print("  --export [file]  Export version info to JSON")
            print("  --changelog [version]  Show changelog")
    else:
        print_version_info()