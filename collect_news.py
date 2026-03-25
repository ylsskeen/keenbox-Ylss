#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Actions 资安新闻收集脚本
自动收集新闻并发送邮件通知
"""

import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import os
import sys

class SecurityNewsCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.news_data = []
        
        # 从环境变量读取邮件配置
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'sender_email': os.getenv('SENDER_EMAIL'),
            'sender_password': os.getenv('SENDER_PASSWORD'),
            'receiver_email': os.getenv('RECEIVER_EMAIL')
        }
        
    def collect_ithome_news(self):
        """收集 iThome 资安新闻"""
        print("\n📰 正在收集 iThome 资安新闻...")
        try:
            url = "https://www.ithome.com.tw/security"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('div', class_='item')
            
            count = 0
            for item in news_items[:10]:
                try:
                    title_tag = item.find('h3') or item.find('h2')
                    if not title_tag:
                        continue
                        
                    link_tag = title_tag.find('a')
                    if not link_tag:
                        continue
                    
                    title = link_tag.text.strip()
                    link = 'https://www.ithome.com.tw' + link_tag['href']
                    
                    time_tag = item.find('time') or item.find('span', class_='date')
                    pub_time = time_tag.text.strip() if time_tag else '未知时间'
                    
                    desc_tag = item.find('p', class_='summary') or item.find('p')
                    description = desc_tag.text.strip() if desc_tag else ''
                    
                    news_item = {
                        'source': 'iThome',
                        'title': title,
                        'link': link,
                        'publish_time': pub_time,
                        'description': description,
                        'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    self.news_data.append(news_item)
                    count += 1
                    print(f"  ✓ {title[:50]}...")
                    
                except Exception as e:
                    continue
                    
            print(f"✅ iThome 收集完成，共 {count} 条")
            
        except Exception as e:
            print(f"❌ 收集 iThome 新闻失败: {e}")
    
    def collect_twcert_news(self):
        """收集 TWCERT 资安新闻"""
        print("\n📰 正在收集 TWCERT 资安新闻...")
        try:
            url = "https://www.twcert.org.tw/tw/lp-104-1.html"
            response = requests.get(url, headers=self.headers, timeout=15)
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, 'html.parser')
            news_items = soup.find_all('div', class_='news_item') or \
                        soup.find_all('li', class_='news') or \
                        soup.find_all('tr')
            
            count = 0
            for item in news_items[:10]:
                try:
                    link_tag = item.find('a')
                    if not link_tag:
                        continue
                    
                    title = link_tag.text.strip()
                    if not title or len(title) < 5:
                        continue
                    
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = 'https://www.twcert.org.tw' + link
                    
                    time_tag = item.find('span', class_='date') or \
                              item.find('td', class_='date') or \
                              item.find('time')
                    pub_time = time_tag.text.strip() if time_tag else '未知时间'
                    
                    news_item = {
                        'source': 'TWCERT',
                        'title': title,
                        'link': link,
                        'publish_time': pub_time,
                        'description': '',
                        'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    self.news_data.append(news_item)
                    count += 1
                    print(f"  ✓ {title[:50]}...")
                    
                except Exception as e:
                    continue
            
            print(f"✅ TWCERT 收集完成，共 {count} 条")
            
        except Exception as e:
            print(f"❌ 收集 TWCERT 新闻失败: {e}")
    
    def generate_html_email(self):
        """生成 HTML 格式的邮件内容"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background: #f5f5f5;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 30px;
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 32px;
                    font-weight: 600;
                }}
                .header p {{
                    margin: 0;
                    opacity: 0.95;
                    font-size: 16px;
                }}
                .stats {{
                    background: #f8f9fa;
                    padding: 20px;
                    text-align: center;
                    border-bottom: 1px solid #e9ecef;
                }}
                .stats-number {{
                    font-size: 36px;
                    font-weight: bold;
                    color: #667eea;
                    margin: 0;
                }}
                .stats-label {{
                    color: #6c757d;
                    margin: 5px 0 0 0;
                }}
                .content {{
                    padding: 30px;
                }}
                .source-section {{
                    margin-bottom: 40px;
                }}
                .source-title {{
                    display: flex;
                    align-items: center;
                    background: #f8f9fa;
                    padding: 15px 20px;
                    border-left: 4px solid #667eea;
                    margin-bottom: 20px;
                    font-size: 20px;
                    font-weight: 600;
                }}
                .source-badge {{
                    background: #667eea;
                    color: white;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-size: 14px;
                    margin-left: auto;
                }}
                .news-item {{
                    background: #fafafa;
                    border: 1px solid #e9ecef;
                    border-radius: 8px;
                    padding: 20px;
                    margin-bottom: 15px;
                    transition: all 0.3s;
                }}
                .news-item:hover {{
                    background: white;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    transform: translateY(-2px);
                }}
                .news-title {{
                    font-size: 18px;
                    font-weight: 600;
                    margin-bottom: 12px;
                    line-height: 1.4;
                }}
                .news-title a {{
                    color: #2c3e50;
                    text-decoration: none;
                }}
                .news-title a:hover {{
                    color: #667eea;
                }}
                .news-meta {{
                    display: flex;
                    align-items: center;
                    color: #6c757d;
                    font-size: 14px;
                    margin-bottom: 10px;
                }}
                .news-description {{
                    color: #555;
                    line-height: 1.6;
                    margin-top: 10px;
                    padding-top: 10px;
                    border-top: 1px solid #e9ecef;
                }}
                .footer {{
                    background: #f8f9fa;
                    text-align: center;
                    padding: 30px;
                    color: #6c757d;
                    font-size: 14px;
                }}
                .footer p {{
                    margin: 5px 0;
                }}
                @media (max-width: 600px) {{
                    body {{
                        padding: 10px;
                    }}
                    .header {{
                        padding: 30px 20px;
                    }}
                    .content {{
                        padding: 20px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 每日资安新闻汇总</h1>
                    <p>{datetime.now().strftime('%Y年%m月%d日 %A')}</p>
                </div>
                
                <div class="stats">
                    <p class="stats-number">{len(self.news_data)}</p>
                    <p class="stats-label">今日共收集资安新闻</p>
                </div>
                
                <div class="content">
        """
        
        # 按来源分组
        for source in ['iThome', 'TWCERT']:
            source_news = [n for n in self.news_data if n['source'] == source]
            if source_news:
                emoji = '📱' if source == 'iThome' else '🛡️'
                html += f"""
                <div class="source-section">
                    <div class="source-title">
                        <span>{emoji} {source}</span>
                        <span class="source-badge">{len(source_news)} 条</span>
                    </div>
                """
                
                for news in source_news:
                    html += f"""
                    <div class="news-item">
                        <div class="news-title">
                            <a href="{news['link']}" target="_blank">{news['title']}</a>
                        </div>
                        <div class="news-meta">
                            📅 {news['publish_time']}
                        </div>
                    """
                    
                    if news['description']:
                        html += f"""
                        <div class="news-description">
                            {news['description']}
                        </div>
                        """
                    
                    html += "</div>"
                
                html += "</div>"
        
        html += f"""
                </div>
                
                <div class="footer">
                    <p><strong>🤖 此邮件由 GitHub Actions 自动发送</strong></p>
                    <p>收集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                    <p>数据来源: iThome 资安频道 & TWCERT/CC</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_email(self):
        """发送邮件通知"""
        if not all([self.email_config['sender_email'], 
                   self.email_config['sender_password'],
                   self.email_config['receiver_email']]):
            print("⚠️  邮件配置不完整，跳过发送")
            return False
            
        print("\n📧 正在发送邮件...")
        try:
            message = MIMEMultipart('alternative')
            message['From'] = Header(f"资安新闻助手 <{self.email_config['sender_email']}>", 'utf-8')
            message['To'] = Header(self.email_config['receiver_email'], 'utf-8')
            message['Subject'] = Header(
                f"📬 每日资安新闻 - {datetime.now().strftime('%Y/%m/%d')} ({len(self.news_data)}条)",
                'utf-8'
            )
            
            html_content = self.generate_html_email()
            html_part = MIMEText(html_content, 'html', 'utf-8')
            message.attach(html_part)
            
            with smtplib.SMTP(self.email_config['smtp_server'], 
                            self.email_config['smtp_port']) as server:
                server.starttls()
                server.login(self.email_config['sender_email'], 
                           self.email_config['sender_password'])
                server.send_message(message)
            
            print(f"✅ 邮件发送成功！已发送到 {self.email_config['receiver_email']}")
            return True
            
        except Exception as e:
            print(f"❌ 邮件发送失败: {e}")
            return False
    
    def save_to_json(self):
        """保存为 JSON 文件"""
        filename = f"security_news_{datetime.now().strftime('%Y%m%d')}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'total': len(self.news_data),
                'news': self.news_data
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 数据已保存: {filename}")
        return filename
    
    def run(self):
        """执行收集任务"""
        print("="*60)
        print(f"🚀 开始收集资安新闻")
        print(f"⏰ 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        # 收集新闻
        self.collect_ithome_news()
        time.sleep(2)
        self.collect_twcert_news()
        
        # 保存数据
        self.save_to_json()
        
        # 发送邮件
        if self.news_data:
            self.send_email()
        else:
            print("\n⚠️  没有收集到新闻")
        
        print("\n" + "="*60)
        print(f"✅ 任务完成！共收集 {len(self.news_data)} 条新闻")
        print("="*60)

if __name__ == "__main__":
    try:
        collector = SecurityNewsCollector()
        collector.run()
    except Exception as e:
        print(f"\n❌ 程序执行失败: {e}")
        sys.exit(1)
