# AI产品每日舆情监控

基于博查Web Search API的AI产品舆情监控工具，自动搜索国内主流AI产品的最新资讯并发送邮件报告。

## 功能特性

- 🤖 **多产品监控**：豆包、腾讯元宝、阿里千问、Qwen、Kimi、智谱
- 📰 **实时资讯**：自动获取最近24小时的舆情资讯
- 🔍 **智能去重**：相似内容自动过滤，保留最新一条
- 📧 **邮件推送**：每日自动发送汇总报告到指定邮箱

## 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `BOCHA_API_KEY` | 博查API Key | ✅ |
| `SMTP_USER` | 发件人邮箱 | ✅ |
| `SMTP_PASSWORD` | SMTP授权码 | ✅ |
| `RECIPIENT` | 收件人邮箱（多个用逗号分隔） | 可选 |
| `SMTP_SERVER` | SMTP服务器（默认: smtp.qq.com） | 可选 |
| `SMTP_PORT` | SMTP端口（默认: 465） | 可选 |

## 使用方法

```bash
# 安装依赖
pip install requests

# 配置环境变量（Linux/Mac）
export BOCHA_API_KEY="your_api_key"
export SMTP_USER="your_email@qq.com"
export SMTP_PASSWORD="your授权码"
export RECIPIENT="recipient@example.com"

# 运行脚本
python skills/ai-social-monitor-bocha/monitor.py
```

## 定时任务（可选）

使用 cron 设置每日自动执行：

```bash
# 每天上午9点执行
0 9 * * * /usr/bin/python3 /path/to/monitor.py >> /var/log/ai-monitor.log 2>&1
```

## 许可证

MIT License