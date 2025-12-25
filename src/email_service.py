"""
email_service.py - Email Digest Service with UTF-8 Support
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List
import re


def clean_text(text):
    """Remove problematic characters while preserving UTF-8"""
    if not text:
        return ""
    text = str(text)
    # Only replace specific problematic characters
    text = text.replace('\xa0', ' ')  # non-breaking space
    text = text.replace('\u200b', '')  # zero-width space
    text = text.replace('\r', '')      # carriage return
    # Keep newlines but normalize them
    text = ' '.join(text.split())
    return text.strip()


class EmailDigestService:
    """Email service for sending paper digests"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.smtp_host = 'smtp.gmail.com'
        self.smtp_port = 587
        self.smtp_user = ''
        self.smtp_password = ''
        self.from_email = ''
        self.from_name = 'Paper Discovery AI'
        self._load_config()
    
    def _load_config(self):
        """Load SMTP config from database"""
        try:
            prefs = self.db.get_preferences()
            if prefs.smtp_host:
                self.smtp_host = prefs.smtp_host
            if prefs.smtp_port:
                self.smtp_port = prefs.smtp_port
            if prefs.smtp_user:
                self.smtp_user = prefs.smtp_user
                self.from_email = prefs.smtp_user
            if prefs.smtp_password:
                self.smtp_password = prefs.smtp_password
        except:
            pass
    
    def configure(self, smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str):
        """Configure and save email settings"""
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_user = smtp_user
        self.smtp_password = smtp_password
        self.from_email = smtp_user
        
        self.db.update_preferences(
            smtp_host=smtp_host,
            smtp_port=smtp_port,
            smtp_user=smtp_user,
            smtp_password=smtp_password
        )
    
    def test_connection(self) -> tuple:
        """Test SMTP connection"""
        try:
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                return True, "Connection successful!"
        except Exception as e:
            return False, str(e)
    
    def _create_paper_html(self, paper) -> str:
        """Create HTML for a single paper"""
        score = paper.relevance_score or paper.user_score or 0
        score_color = '#10b981' if score >= 0.7 else '#3b82f6' if score >= 0.5 else '#8b5cf6'
        
        # Clean all text fields
        title = clean_text(paper.title or 'Untitled')[:150]
        authors = clean_text(paper.authors or 'Unknown')[:80]
        summary = clean_text(paper.summary or '')[:250]
        category = clean_text(paper.primary_category or 'Unknown')
        pdf_url = paper.pdf_url or '#'
        abs_url = paper.abs_url or '#'
        
        return f"""
        <div style="background: #ffffff; border-radius: 16px; padding: 24px; margin: 16px 0; 
                    border-left: 4px solid {score_color}; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span style="background: {score_color}; color: white; padding: 6px 14px; border-radius: 20px; 
                            font-size: 13px; font-weight: 600;">{score:.0%} Match</span>
                <span style="color: #64748b; font-size: 13px;">{category}</span>
            </div>
            <h3 style="margin: 0 0 12px; color: #1e293b; font-size: 18px; line-height: 1.4;">
                <a href="{abs_url}" style="color: #1e293b; text-decoration: none;">{title}</a>
            </h3>
            <p style="color: #64748b; font-size: 14px; margin: 0 0 12px;">{authors}</p>
            <p style="color: #475569; font-size: 14px; line-height: 1.6; margin: 0 0 16px;">{summary}...</p>
            <div>
                <a href="{pdf_url}" style="background: {score_color}; color: white; padding: 10px 20px; 
                        border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600; 
                        margin-right: 10px;">Read PDF</a>
                <a href="{abs_url}" style="background: #f1f5f9; color: #475569; padding: 10px 20px; 
                        border-radius: 8px; text-decoration: none; font-size: 14px; font-weight: 600;">arXiv</a>
            </div>
        </div>
        """
    
    def _create_digest_html(self, papers: List, digest_type: str) -> str:
        """Create full digest HTML email"""
        papers_html = '\n'.join([self._create_paper_html(p) for p in papers])
        
        interests = self.db.get_user_interests()
        top_categories = list(interests['categories'].keys())[:3]
        
        interests_html = ""
        if top_categories:
            # Clean each category name
            cats_text = ', '.join([clean_text(c) for c in top_categories])
            interests_html = f"""
            <div style="background: #f8fafc; border-radius: 12px; padding: 16px; margin: 20px 0;">
                <p style="margin: 0; color: #64748b; font-size: 14px;">
                    Your interests: {cats_text}
                </p>
            </div>
            """
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                    background: #f1f5f9; margin: 0; padding: 0;">
            <div style="max-width: 680px; margin: 0 auto; padding: 40px 20px;">
                <div style="text-align: center; margin-bottom: 40px;">
                    <h1 style="margin: 0; color: #1e293b; font-size: 28px; font-weight: 800;">
                        Your {digest_type.title()} Research Digest
                    </h1>
                    <p style="color: #64748b; font-size: 16px; margin: 12px 0 0;">
                        {len(papers)} new papers matching your interests
                    </p>
                </div>
                {interests_html}
                <div style="margin: 30px 0;">{papers_html}</div>
                <div style="text-align: center; padding: 30px 0; border-top: 1px solid #e2e8f0; margin-top: 40px;">
                    <p style="color: #94a3b8; font-size: 13px; margin: 0;">
                        Generated by Paper Discovery AI based on your research interests.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def send_digest(self, to_email: str, papers: List, digest_type: str = 'daily') -> tuple:
        """Send digest email"""
        if not papers:
            return False, "No papers to send"
        
        self._load_config()
        
        if not self.smtp_user or not self.smtp_password:
            return False, "Email not configured. Set SMTP credentials in Settings."
        
        try:
            # Create message with UTF-8 encoding from the start
            msg = MIMEMultipart('alternative')
            msg.set_charset('utf-8')
            
            # Clean email addresses
            to_email = clean_text(to_email)
            
            msg['Subject'] = f"Your {digest_type.title()} Research Digest - {len(papers)} New Papers"
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            html_content = self._create_digest_html(papers, digest_type)
            
            plain_text = f"Your {digest_type} research digest\n\n"
            for p in papers:
                title = clean_text(p.title or 'Untitled')
                plain_text += f"- {title}\n  {p.abs_url}\n\n"
            
            # Attach parts with explicit UTF-8 encoding
            part1 = MIMEText(plain_text, 'plain', 'utf-8')
            part2 = MIMEText(html_content, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Send with UTF-8 support
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                # Use send_message instead of sendmail for better UTF-8 handling
                server.send_message(msg)
            
            paper_ids = [p.arxiv_id for p in papers]
            self.db.record_digest(paper_ids, digest_type, 'sent')
            
            return True, f"Digest sent to {to_email}"
            
        except Exception as e:
            self.db.record_digest([], digest_type, 'failed')
            return False, str(e)
    
    def send_test_email(self, to_email: str) -> tuple:
        """Send a test email"""
        self._load_config()
        
        if not self.smtp_user or not self.smtp_password:
            return False, "SMTP not configured"
        
        try:
            # Create message with UTF-8 encoding
            msg = MIMEMultipart('alternative')
            msg.set_charset('utf-8')
            
            # Clean email address
            to_email = clean_text(to_email)
            
            msg['Subject'] = "Test Email from Paper Discovery"
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            html = """
            <!DOCTYPE html>
            <html>
            <head><meta charset="utf-8"></head>
            <body>
            <div style="font-family: sans-serif; max-width: 500px; margin: 0 auto; padding: 40px;">
                <div style="text-align: center;">
                    <h1 style="color: #10b981; font-size: 48px; margin: 0;">✓ Success!</h1>
                    <h2 style="color: #1e293b;">Email Works!</h2>
                    <p style="color: #64748b;">Your Paper Discovery email integration is working correctly.</p>
                </div>
            </div>
            </body>
            </html>
            """
            
            plain = "Test email from Paper Discovery - it works!"
            
            # Attach with explicit UTF-8 encoding
            part1 = MIMEText(plain, 'plain', 'utf-8')
            part2 = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True, "Test email sent successfully!"
        except Exception as e:
            return False, str(e)