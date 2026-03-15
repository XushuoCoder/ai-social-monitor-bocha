"""
邮件发送脚本 - 用于舆情监控报告推送
自动搜索豆包/元宝/千问最近24小时舆情并发送邮件
"""
import smtplib
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import os
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta, timezone
from difflib import SequenceMatcher

# ========== 配置 ==========
# 博查API配置（支持环境变量）
BOCHA_API_KEY = os.environ.get("BOCHA_API_KEY", "")
BOCHA_API_URL = "https://api.bocha.cn/v1/web-search"

# 邮件配置（支持环境变量）
SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.qq.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")  # SMTP授权码

# ========== 收件人配置（直接修改这里）==========
# 支持多个邮箱，用英文逗号分隔
DEFAULT_RECIPIENT = "xushuo@huawei.com"

# 解析收件人（支持多邮箱，逗号分隔）
def parse_recipients(recipient_str):
    """解析收件人字符串，支持多个邮箱"""
    if not recipient_str:
        return []
    # 按逗号分隔并去除空格
    return [email.strip() for email in recipient_str.split(',') if email.strip()]

RECIPIENT_LIST = parse_recipients(os.environ.get("RECIPIENT", DEFAULT_RECIPIENT))
# 保持向后兼容：RECIPIENT 仍作为字符串（首个收件人）
RECIPIENT = RECIPIENT_LIST[0] if RECIPIENT_LIST else ""
SENDER = SMTP_USER

# 检查必要配置
if not BOCHA_API_KEY or not SMTP_USER or not SMTP_PASSWORD:
    print("❌ 错误: 请设置必要的环境变量")
    print("需要的环境变量:")
    print("  - BOCHA_API_KEY: 博查API Key")
    print("  - SMTP_USER: 发件人邮箱")
    print("  - SMTP_PASSWORD: SMTP授权码")
    print("\n可选环境变量:")
    print("  - RECIPIENT: 收件人邮箱 (默认: xushuo@huawei.com)")
    print("  - SMTP_SERVER: SMTP服务器 (默认: smtp.qq.com)")
    print("  - SMTP_PORT: SMTP端口 (默认: 465)")
    sys.exit(1)

# 搜索关键词
SEARCH_KEYWORDS = ["豆包", "腾讯元宝", "阿里千问", "qwen", "kimi", "智谱"]

# 排除关键词（过滤不相关内容）
EXCLUDE_KEYWORDS = [
    "豆干", "豆浆", "豆腐", "豆花", "豆香", "豆皮",  # 食品类
    "黄豆", "黑豆", "红豆", "绿豆",  # 豆类
    "豆奶粉", "豆奶", "豆油", "酱油",
    "豆蔻", "豆苗", "豆芽",
    "兔宝宝", "油漆", "板材", "装饰",  # 品牌名误匹配
    "海底捞", "酒店", "餐饮", "做饭", "早餐",  # 无关内容
    "球场围栏", "操场", "球场", "围栏",  # 误匹配
    "研究生院", "大学", "学院", "招生",  # 误匹配
    "股票", "股价", "证券", "基金", "行情",  # 股票内容
]


def should_exclude(title, summary):
    """检查内容是否应该被排除"""
    text = (title + " " + summary).lower()
    for keyword in EXCLUDE_KEYWORDS:
        if keyword.lower() in text:
            return True
    return False


def similarity(a, b):
    """计算两个字符串的相似度 (0-1)"""
    if not a or not b:
        return 0
    return SequenceMatcher(None, a, b).ratio()


def filter_similar(news_list, threshold=0.6):
    """过滤相似或重复的新闻，保留最新的一条"""
    filtered = []
    for news in news_list:
        # 排除不相关内容
        if should_exclude(news.get('title', ''), news.get('summary', '')):
            continue
            
        is_duplicate = False
        news_title = news.get('title', '')
        news_summary = news.get('summary', '')
        
        for existing in filtered:
            existing_title = existing.get('title', '')
            existing_summary = existing.get('summary', '')
            
            # 标题相似度 > 60% 视为重复
            title_sim = similarity(news_title, existing_title)
            # 摘要相似度 > 60% 视为重复
            summary_sim = similarity(news_summary, existing_summary)
            
            if title_sim > threshold or summary_sim > threshold:
                is_duplicate = True
                # 如果是重复的，保留日期更新的那个
                existing_date = existing.get('date', '')
                news_date = news.get('date', '')
                if news_date > existing_date:
                    filtered.remove(existing)
                    filtered.append(news)
                break
        
        if not is_duplicate:
            filtered.append(news)
    
    return filtered


# ========== 舆情搜索 ==========
def search_news(keyword, hours=24):
    """搜索最近24小时的新闻舆情"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {BOCHA_API_KEY}"
    }
    
    payload = {
        "query": keyword,
        "summary": True,
        "freshness": "oneDay",
        "count": 20
    }
    
    try:
        response = requests.post(BOCHA_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        now = datetime.now(timezone.utc)
        cutoff_time = now - timedelta(hours=hours)
        
        results = []
        if data.get("code") == 200 and data.get("data", {}).get("webPages", {}).get("value"):
            for item in data["data"]["webPages"]["value"]:
                date_str = item.get("datePublished", "")
                if date_str:
                    try:
                        pub_date = parse_date(date_str)
                        if pub_date and pub_date.tzinfo is None:
                            pub_date = pub_date.replace(tzinfo=timezone.utc)
                        if pub_date and pub_date >= cutoff_time:
                            results.append({
                                "title": item.get("name", ""),
                                "url": item.get("url", ""),
                                "summary": item.get("summary", "")[:200],
                                "date": date_str
                            })
                    except Exception:
                        pass
        
        return results
    except Exception as e:
        print(f"搜索错误 [{keyword}]: {e}")
        return []


def parse_date(date_str):
    """解析多种日期格式"""
    formats = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S+08:00",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None


def generate_report(news_dict):
    """生成舆情报告"""
    report_lines = []
    report_lines.append("=" * 60)
    report_lines.append(f"📊 AI产品每日舆情监控报告")
    report_lines.append(f"📅 统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"📈 搜索关键词: {', '.join(SEARCH_KEYWORDS)}")
    report_lines.append("=" * 60)
    report_lines.append("")
    
    total_count = 0
    for keyword in SEARCH_KEYWORDS:
        news_list = news_dict.get(keyword, [])
        total_count += len(news_list)
        report_lines.append(f"\n### 🔍 {keyword} (共{len(news_list)}条)")
        report_lines.append("-" * 40)
        
        if not news_list:
            report_lines.append("  ⚠️ 暂无最新舆情")
        else:
            for i, news in enumerate(news_list[:10], 1):
                title = news["title"][:60] + "..." if len(news["title"]) > 60 else news["title"]
                url = news.get("url", "")
                date = news["date"][:10] if news["date"] else ""
                report_lines.append(f"\n  {i}. {title}")
                if url:
                    report_lines.append(f"     🔗 {url}")
                if date:
                    report_lines.append(f"     📅 {date}")
                if news["summary"]:
                    summary = news["summary"][:80] + "..." if len(news["summary"]) > 80 else news["summary"]
                    report_lines.append(f"     📝 {summary}")
    
    report_lines.append("\n" + "=" * 60)
    report_lines.append(f"📊 汇总: 共获取 {total_count} 条舆情")
    report_lines.append("=" * 60)
    
    return "\n".join(report_lines)


# ========== 邮件发送 ==========
def send_email(body_content):
    """发送邮件"""
    global RECIPIENT_LIST
    
    subject = f"国内AI产品每日资讯汇总-{datetime.now().strftime('%Y/%m/%d')}"
    
    # 支持多收件人
    to_address = ", ".join(RECIPIENT_LIST) if len(RECIPIENT_LIST) > 1 else RECIPIENT_LIST[0]
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = SENDER
    msg['To'] = to_address
    
    text_content = body_content.replace('\n\n', '\n')
    msg.attach(MIMEText(text_content, 'plain', 'utf-8'))
    
    html_content = body_content.replace('\n', '<br>')
    html_content = f"""
    <html>
    <body>
    <pre style="font-family: Arial, sans-serif; font-size: 14px; line-height: 1.6;">
    {html_content}
    </pre>
    </body>
    </html>
    """
    msg.attach(MIMEText(html_content, 'html', 'utf-8'))
    
    try:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SENDER, RECIPIENT_LIST, msg.as_string())
        server.quit()
        
        print(f"✅ 邮件发送成功: {', '.join(RECIPIENT_LIST)}")
        return True
    except Exception as e:
        print(f"❌ 邮件发送失败: {e}")
        return False


# ========== 主程序 ==========
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 开始舆情监控...")
    print("=" * 50)
    
    # 搜索各关键词舆情
    news_dict = {}
    for keyword in SEARCH_KEYWORDS:
        print(f"🔍 搜索: {keyword} ...")
        news = search_news(keyword, hours=24)
        # 去重过滤
        news = filter_similar(news, threshold=0.6)
        news_dict[keyword] = news
        print(f"   去重后: {len(news)} 条")
    
    # 生成报告
    report = generate_report(news_dict)
    print("\n" + report)
    
    # 发送邮件
    print("\n📤 发送邮件...")
    send_email(report)