#!/bin/bash
# Quick Setup Script for Local Testing Configuration

echo "⚙️  Gmail Send Skill - Local Testing Setup"
echo "=========================================="

# Check if config_local.json already exists
if [ -f "config_local.json" ]; then
    echo "📋 config_local.json already exists"
    read -p "Do you want to overwrite it? (y/N): " -r
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "✋ Setup cancelled"
        exit 0
    fi
fi

# Copy template to local config
if [ -f "config_template.json" ]; then
    cp config_template.json config_local.json
    echo "✅ Created config_local.json from template"
else
    echo "❌ config_template.json not found"
    exit 1
fi

# Interactive configuration
echo ""
echo "📝 Please provide the following information:"
echo ""

# Gmail username
read -p "📧 Your Gmail address: " gmail_username
if [ -n "$gmail_username" ]; then
    # Use sed to replace the placeholder in JSON
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your\.email@gmail\.com/$gmail_username/g" config_local.json
    else
        # Linux
        sed -i "s/your\.email@gmail\.com/$gmail_username/g" config_local.json
    fi
    echo "✅ Gmail address set: $gmail_username"
fi

# App Password
echo ""
echo "🔐 Gmail App Password Setup:"
echo "   1. Go to https://myaccount.google.com/"
echo "   2. Security → 2-Step Verification → App Passwords"
echo "   3. Select 'Mail' and generate password"
echo "   4. Copy the 16-character password"
echo ""
read -p "🔑 Your Gmail App Password (16 chars): " gmail_app_password
if [ -n "$gmail_app_password" ]; then
    # Clean the password (remove spaces)
    clean_password=$(echo "$gmail_app_password" | tr -d ' ')
    
    if [ ${#clean_password} -eq 16 ]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS - escape special characters for sed
            escaped_password=$(printf '%s\n' "$gmail_app_password" | sed 's/[[\.*^$(){}?+|]/\\&/g')
            sed -i '' "s/REPLACE_WITH_YOUR_16_CHAR_APP_PASSWORD/$escaped_password/g" config_local.json
        else
            # Linux
            escaped_password=$(printf '%s\n' "$gmail_app_password" | sed 's/[[\.*^$(){}?+|]/\\&/g')
            sed -i "s/REPLACE_WITH_YOUR_16_CHAR_APP_PASSWORD/$escaped_password/g" config_local.json
        fi
        echo "✅ App Password configured"
    else
        echo "⚠️  Warning: App Password should be 16 characters. You entered ${#clean_password} characters."
        echo "📝 You may need to manually edit config_local.json"
    fi
fi

# Test recipient email
echo ""
read -p "📮 Test recipient email: " test_email
if [ -n "$test_email" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/recipient@example\.com/$test_email/g" config_local.json
    else
        # Linux
        sed -i "s/recipient@example\.com/$test_email/g" config_local.json
    fi
    echo "✅ Test recipient set: $test_email"
fi

# Display name
echo ""
read -p "👤 Your display name (optional): " display_name
if [ -n "$display_name" ]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/Your Display Name/$display_name/g" config_local.json
    else
        # Linux
        sed -i "s/Your Display Name/$display_name/g" config_local.json
    fi
    echo "✅ Display name set: $display_name"
fi

# Enable real sending option
echo ""
read -p "🚀 Enable real email sending? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' 's/"enable_real_send": false/"enable_real_send": true/g' config_local.json
    else
        # Linux
        sed -i 's/"enable_real_send": false/"enable_real_send": true/g' config_local.json
    fi
    echo "✅ Real email sending enabled"
else
    echo "📋 Real email sending disabled (dry run mode)"
fi

echo ""
echo "🎉 Local testing configuration complete!"
echo ""
echo "Next steps:"
echo "  1. Test basic functionality:     python3 test_local.py --basic"
echo "  2. Test parameters (dry run):    python3 test_local.py --dry-run"
echo "  3. Send real test email:         python3 test_local.py --send"
echo "  4. Interactive testing:          python3 test_local.py"
echo ""
echo "📝 To modify settings later, edit config_local.json"
echo "🔒 Remember: config_local.json contains sensitive data and won't be uploaded to Git"