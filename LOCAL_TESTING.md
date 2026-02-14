# Local Testing Guide - Gmail Send Skill

本文档说明如何在本地安全地测试 Gmail Send Skill，而不会将敏感信息上传到代码仓库。

## 🔧 快速设置

### 1. 自动化设置（推荐）

```bash
# 运行自动化设置脚本
./setup_local_config.sh
```

脚本会引导您：
- 输入 Gmail 地址
- 配置 App Password
- 设置测试收件人
- 选择显示名称
- 启用/禁用实际邮件发送

### 2. 手动设置

```bash
# 复制配置模板
cp config_template.json config_local.json

# 编辑配置文件
nano config_local.json  # 或使用您喜欢的编辑器
```

在 `config_local.json` 中填入：
- `gmail_config.username`: 您的 Gmail 地址
- `gmail_config.app_password`: 16位 App Password
- `test_config.to_email`: 测试收件人地址
- `gmail_config.from_name`: 发件人显示名称

## 🧪 测试选项

### 基本功能测试

```bash
# 测试技能基本功能（无网络请求）
python3 test_local.py --basic
```

### 参数验证测试（模拟测试）

```bash
# 验证参数但不发送邮件
python3 test_local.py --dry-run
```

### 实际邮件发送测试

```bash
# 发送真实邮件（需要在配置中启用）
python3 test_local.py --send
```

### 交互式测试

```bash
# 启动交互式测试菜单
python3 test_local.py
```

交互式菜单包含：
1. 基本功能测试
2. 邮件参数测试（模拟）
3. 发送真实邮件
4. 查看当前配置
5. 退出

## 📋 配置文件说明

### config_local.json 结构

```json
{
  "gmail_config": {
    "username": "your.email@gmail.com",
    "app_password": "abcd efgh ijkl mnop",
    "from_name": "Your Display Name"
  },
  "test_config": {
    "to_email": "recipient@example.com",
    "test_subject": "Gmail Send Skill Test Email",
    "test_content_markdown": "# 测试邮件内容..."
  },
  "smtp_config": {
    "smtp_server": "smtp.gmail.com",
    "smtp_port": 587,
    "use_tls": true,
    "timeout": 30
  },
  "testing": {
    "enable_real_send": false,
    "mock_mode": true,
    "log_level": "INFO"
  }
}
```

### 重要字段说明

- **`enable_real_send`**: 设为 `true` 才能发送真实邮件
- **`mock_mode`**: 设为 `true` 启用模拟模式
- **`test_content_markdown`**: 支持完整 Markdown 语法的邮件内容

## 🔐 Gmail App Password 设置

### 步骤

1. **启用两步验证**
   - 访问 [Google 账户设置](https://myaccount.google.com/)
   - 转到"安全性" → "两步验证"
   - 启用两步验证

2. **生成应用专用密码**
   - 在"两步验证"页面，找到"应用专用密码"
   - 选择"邮件"应用
   - 生成密码
   - 复制16位密码（格式如：`abcd efgh ijkl mnop`）

3. **在配置中使用**
   - 将密码填入 `config_local.json` 的 `app_password` 字段
   - 密码可以包含空格或不包含空格

## 🧪 测试示例

### 基本功能测试示例

```bash
$ python3 test_local.py --basic
🧪 Gmail Send Skill - Local Testing
====================================

🧪 Testing Basic Skill Functionality...
✅ Schema validation passed
✅ MCP resources available
```

### 参数验证测试示例

```bash
$ python3 test_local.py --dry-run
🧪 Gmail Send Skill - Local Testing
====================================

✅ Configuration loaded from: config_local.json
✅ Configuration validation passed

📧 Testing Email Send (DRY RUN)...
📋 Test Parameters:
   • From: Your Name <your.email@gmail.com>
   • To: test@example.com
   • Subject: Gmail Send Skill Test Email
   • Content: 892 characters
   • App Password: ************mnop
✅ Parameter validation passed
🎯 Ready for real email sending!
```

### 交互式测试示例

```bash
$ python3 test_local.py
🧪 Gmail Send Skill - Local Testing
====================================

🎮 Interactive Test Menu
========================
1. Basic functionality test
2. Email parameters test (dry run)
3. Send real email
4. View configuration
5. Exit

Select option (1-5): 2
✅ Configuration loaded from: config_local.json
✅ Configuration validation passed
📧 Testing Email Send (DRY RUN)...
...
🎉 Parameters test passed!
```

## 📧 邮件内容测试

配置文件包含一个丰富的 Markdown 邮件模板，用于测试：

- ✅ 标题和子标题
- ✅ **粗体** 和 *斜体* 文本
- ✅ `代码格式`
- ✅ 链接
- ✅ 有序和无序列表
- ✅ 引用块
- ✅ 表情符号

您可以修改 `test_content_markdown` 来测试自定义内容。

## 🔒 安全提醒

### ⚠️ 重要安全事项

1. **不要提交敏感文件**
   - `config_local.json` 已在 `.gitignore` 中排除
   - 绝不要将包含真实凭据的文件提交到 Git

2. **保护 App Password**
   - App Password 与常规密码同等重要
   - 定期轮换 App Password
   - 为不同应用使用不同的 App Password

3. **测试安全**
   - 使用您自己的邮箱作为测试收件人
   - 避免向他人发送测试邮件
   - 在测试环境中先进行模拟测试

## 🛠️ 故障排除

### 常见问题

#### 配置文件不存在
```
❌ Configuration file not found: config_local.json
📝 Please copy config_template.json to config_local.json and fill in your details
```
**解决方案**: 运行 `./setup_local_config.sh` 或手动复制模板文件

#### App Password 格式错误
```
❌ Invalid App Password format. Should be 16 alphanumeric characters
📝 Example: 'abcd efgh ijkl mnop' or 'abcdefghijklmnop'
```
**解决方案**: 确保 App Password 正好是16个字母数字字符

#### 验证失败
```
❌ Missing or incomplete configuration fields:
   • gmail_config.app_password
```
**解决方案**: 检查配置文件中是否包含 `REPLACE_WITH` 占位符，需要替换为实际值

#### 实际发送被禁用
```
⚠️  Real sending is disabled in configuration
📝 Set 'testing.enable_real_send' to true in config_local.json
```
**解决方案**: 在配置文件中将 `enable_real_send` 设为 `true`

## 📁 文件结构

```
mcp-server-gmail-send/
├── config_template.json       # 安全模板（可提交）
├── config_local.json         # 本地配置（不提交）
├── test_local.py             # 本地测试脚本
├── setup_local_config.sh     # 自动设置脚本
└── LOCAL_TESTING.md          # 本文档
```

## 🤝 开发工作流程

1. **初始设置**: `./setup_local_config.sh`
2. **基本测试**: `python3 test_local.py --basic`
3. **参数测试**: `python3 test_local.py --dry-run`
4. **实际测试**: `python3 test_local.py --send`
5. **开发调试**: `python3 test_local.py` (交互模式)

这个工作流程确保您可以安全地测试技能功能，而不会意外泄露敏感信息。