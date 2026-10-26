from datetime import datetime, timedelta, timezone
from flask_mail import Message
from flask import url_for
import hashlib
import secrets

from ..models.email_verification import EmailVerification
from ..models.password_reset_token import PasswordResetToken
from ..extensions import mail, db
from ..models.user import User


def create_verification_token() -> tuple[str, str]:
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    return token, token_hash


def fmt_timedelta(delta: timedelta) -> str:
    parts = []

    def add_val_if_nonzero(val: int, units: str) -> None:
        if val:
            parts.append(f'{val} {units}{"s" if val != 1 else ""}')

    add_val_if_nonzero(delta.days, 'day')

    hours, remainder = divmod(delta.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    add_val_if_nonzero(hours,   'hour')
    add_val_if_nonzero(minutes, 'minute')
    add_val_if_nonzero(seconds, 'second')

    return ', '.join(parts) or '0 seconds'


def create_and_send_email_verification(user: User, time_til_expiration: timedelta=timedelta(minutes=15)) -> None:
    # remove any existing verification for this user
    existing = EmailVerification.get_one_or_none_by(user_id=user.id)
    if existing is not None:
        db.session.delete(existing)
        db.session.flush()

    # create token and hash of token
    token, token_hash = create_verification_token()

    # create the DB entry
    expiration_time = datetime.now(timezone.utc) + time_til_expiration
    verification = EmailVerification(user_id=user.id, token_hash=token_hash, expires_at=expiration_time)

    # put the email verification entry into the DB
    db.session.add(verification)
    db.session.commit()

    # generate authentication URL
    verification_url = url_for('account.verify_email', token=token, _external=True)

    # create email
    subject = 'LPM Tenant Union Email Verification'
    msg = Message(subject=subject, recipients=[user.email])

    # fill out the body
    msg.body  = f'Hello {user.name},\n\n'
    msg.body +=  'Please verify your email address by clicking the link below:\n\n'
    msg.body += f'{verification_url}\n\n'
    msg.body += f'This link will expire in {fmt_timedelta(time_til_expiration)}.\n\n'
    msg.body +=  'If you didn\'t create an account, you can safely ignore this email.\n'

    # send email
    mail.send(msg)


def create_and_send_password_reset(user: User, time_til_expiration: timedelta=timedelta(minutes=15), ip_address: str | None = None) -> None:
    from ..models.password_reset_token import PasswordResetToken

    # remove any existing password reset token for this user
    existing = PasswordResetToken.get_one_or_none_by(user_id=user.id)
    if existing is not None:
        db.session.delete(existing)
        db.session.flush()

    # create token and hash of token
    token, token_hash = create_verification_token()

    # create the DB entry
    expiration_time = datetime.now(timezone.utc) + time_til_expiration
    reset_token = PasswordResetToken(user_id=user.id, token_hash=token_hash, expires_at=expiration_time, ip_address=ip_address)

    # put the password reset token entry into the DB
    db.session.add(reset_token)
    db.session.commit()

    # generate password reset URL
    reset_url = url_for('account.reset_password', token=token, _external=True)

    # create email
    subject = 'Password Reset Request - LPM Tenant Union'
    msg = Message(subject=subject, recipients=[user.email])

    # fill out the body
    msg.body = f'Hello {user.name},\n\n'
    msg.body += 'We received a request to reset your password for your LPM Tenant Union account.\n\n'
    msg.body += 'To reset your password, please click the link below:\n\n'
    msg.body += f'{reset_url}\n\n'
    msg.body += f'This link will expire in {fmt_timedelta(time_til_expiration)}.\n\n'
    msg.body += 'IMPORTANT SECURITY NOTICE:\n'
    msg.body += '- Do not share this link with anyone.\n'
    msg.body += '- Only you can use this link to reset your password.\n'
    msg.body += '- If you did not request a password reset, you can safely ignore this email.\n'
    msg.body += '- Your password will remain unchanged if you do not use this link.\n'
    msg.body += '\nThank you,\nLPM Tenant Union'

    # send email
    mail.send(msg)
