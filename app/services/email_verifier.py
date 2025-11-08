"""
Email verification service.
Validates email addresses using DNS MX records and SMTP checks.
"""
import smtplib
import dns.resolver
from typing import Tuple
import socket

from app.config import settings


def verify_email_async(email: str) -> bool:
    """
    Verify if an email address is valid and deliverable.

    Performs:
    1. Format validation
    2. DNS MX record check
    3. SMTP connection test (without sending email)

    Args:
        email: Email address to verify

    Returns:
        True if email appears valid, False otherwise
    """
    if not email or '@' not in email:
        return False

    try:
        # Split email
        local_part, domain = email.rsplit('@', 1)

        # Step 1: Check DNS MX records
        mx_valid, mx_host = check_mx_record(domain)
        if not mx_valid:
            return False

        # Step 2: SMTP verification (if enabled)
        if settings.SMTP_VERIFY_ENABLED:
            smtp_valid = check_smtp(email, mx_host)
            return smtp_valid

        # If SMTP check disabled, MX record is enough
        return True

    except Exception as e:
        print(f"Email verification error for {email}: {e}")
        return False


def check_mx_record(domain: str) -> Tuple[bool, str]:
    """
    Check if domain has valid MX records.

    Args:
        domain: Email domain

    Returns:
        Tuple of (is_valid, mx_host)
    """
    try:
        mx_records = dns.resolver.resolve(domain, 'MX')
        if not mx_records:
            return False, None

        # Get the MX record with highest priority (lowest preference number)
        mx_record = min(mx_records, key=lambda r: r.preference)
        mx_host = str(mx_record.exchange).rstrip('.')

        return True, mx_host

    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers):
        return False, None
    except Exception as e:
        print(f"MX check error for {domain}: {e}")
        return False, None


def check_smtp(email: str, mx_host: str) -> bool:
    """
    Verify email via SMTP connection.

    This performs a "soft" check:
    - Connects to mail server
    - Sends HELO/EHLO
    - Sends MAIL FROM
    - Sends RCPT TO (to check if mailbox exists)
    - Does NOT send actual email

    Args:
        email: Email address to verify
        mx_host: MX host to connect to

    Returns:
        True if email appears deliverable
    """
    try:
        # Connect to mail server
        server = smtplib.SMTP(timeout=settings.SMTP_TIMEOUT)
        server.connect(mx_host)

        # EHLO/HELO
        server.helo(server.local_hostname)

        # MAIL FROM
        server.mail(settings.EMAIL_VERIFICATION_FROM)

        # RCPT TO - this checks if mailbox exists
        code, message = server.rcpt(email)

        # Close connection
        server.quit()

        # 250 = success, 251 = user not local (but will forward)
        return code in [250, 251]

    except smtplib.SMTPServerDisconnected:
        return False
    except smtplib.SMTPConnectError:
        return False
    except socket.timeout:
        return False
    except Exception as e:
        print(f"SMTP verification error for {email}: {e}")
        return False


def is_disposable_email(email: str) -> bool:
    """
    Check if email is from a disposable email provider.

    Args:
        email: Email address

    Returns:
        True if disposable
    """
    if '@' not in email:
        return False

    domain = email.split('@')[1].lower()

    # Common disposable email domains
    disposable_domains = [
        'guerrillamail.com',
        'mailinator.com',
        '10minutemail.com',
        'tempmail.com',
        'throwaway.email',
        'yopmail.com',
    ]

    return domain in disposable_domains
