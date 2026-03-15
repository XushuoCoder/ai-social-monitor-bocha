# AI产品每日舆情监控

基于博查Web Search API的AI产品舆情监控工具，自动搜索国内主流AI产品的最新资讯并发送邮件报告。

## 📋 项目简介

本工具适用于：
- 📢 **运营人员**：追踪AI产品最新动态，了解竞品资讯
- 🔍 **行业研究者**：收集AI产品舆情数据，进行市场分析
- 🤖 **AI爱好者**：第一时间掌握豆包、元宝、千问等产品的最新消息

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🤖 多产品监控 | 豆包、腾讯元宝、阿里千问、Qwen、Kimi、智谱 |
| 📰 实时资讯 | 自动获取最近24小时的舆情资讯 |
| 🔍 智能去重 | 相似内容自动过滤，保留最新一条 |
| 📧 邮件推送 | 每日自动发送汇总报告到指定邮箱 |
| 🚫 垃圾过滤 | 自动排除无关内容（如食品"豆干"、股票等） |

## 🛠️ 环境配置

### 1. 博查API Key 申请

1. 访问 [博查AI开放平台](https://www.bochaai.com/)
2. 注册账号并登录
3. 在控制台创建API Key
4. 复制Key备用

### 2. SMTP邮箱设置

以QQ邮箱为例：
1. 登录QQ邮箱 → 设置 → 账户
2. 开启"POP3/SMTP服务"
3. 获取**授权码**（不是登录密码）

### 3. 环境变量

| 变量名 | 说明 | 必需 |
|--------|------|------|
| `BOCHA_API_KEY` | 博查API Key | ✅ |
| `SMTP_USER` | 发件人邮箱（如 1060509640@qq.com） | ✅ |
| `SMTP_PASSWORD` | SMTP授权码 | ✅ |
| `RECIPIENT` | 收件人邮箱（多个用逗号分隔） | 可选 |
| `SMTP_SERVER` | SMTP服务器（默认: smtp.qq.com） | 可选 |
| `SMTP_PORT` | SMTP端口（默认: 465） | 可选 |

## 🚀 快速开始

### Windows

```cmd
# 配置环境变量
set BOCHA_API_KEY=你的博查APIKey
set SMTP_USER=你的邮箱@qq.com
set SMTP_PASSWORD=你的授权码
set RECIPIENT=收件人邮箱

# 运行
python skills\ai-social-monitor-bocha\monitor.py
```

### Linux/Mac

```bash
# 配置环境变量
export BOCHA_API_KEY="your_api_key"
export SMTP_USER="your_email@qq.com"
export SMTP_PASSWORD="your授权码"
export RECIPIENT="recipient@example.com"

# 运行
python skills/ai-social-monitor-bocha/monitor.py
```

## ⏰ 定时任务

### Windows 任务计划程序

1. 打开"任务计划程序"
2. 创建基本任务 → 命名"AI舆情监控"
3. 触发器：每天 → 设置时间（如9:00）
4. 操作：启动程序 → Python路径 + 脚本路径

### Linux/Mac cron

```bash
# 每天上午9点执行
0 9 * * * /usr/bin/python3 /path/to/monitor.py >> /var/log/ai-monitor.log 2>&1
```

## 📊 邮件示例

收到的邮件标题格式：
```
国内AI产品每日资讯汇总-2026/03/15
```

邮件内容包含：
- 各产品资讯条数统计
- 每条资讯的标题、链接、发布时间、摘要
- 去重后的汇总数量

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License
