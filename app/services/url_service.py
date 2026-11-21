
import secrets
import string

from sqlalchemy.orm import Session

from app.models import URL


def generate_short_code(length=7):

    characters = string.ascii_letters + string.digits

    return ''.join(
        secrets.choice(characters)
        for _ in range(length)
    )


def create_short_url(
    db: Session,
    original_url: str,
    custom_alias: str | None = None,
    expires_at=None
):

    # Handle custom aliases
    if custom_alias:

        existing = db.query(URL).filter(
            URL.short_code == custom_alias
        ).first()

        if existing:
            raise ValueError("Custom alias already exists")

        short_code = custom_alias

    else:

        # Generate a unique short code
        short_code = generate_short_code()

        while db.query(URL).filter(
            URL.short_code == short_code
        ).first():

            short_code = generate_short_code()

    # Create SQLAlchemy object
    new_url = URL(
        original_url=original_url,
        short_code=short_code,
        expires_at=expires_at
    )

    # Save to database
    db.add(new_url)
    db.commit()

    # Retrieve database-generated values
    db.refresh(new_url)

    return new_url
