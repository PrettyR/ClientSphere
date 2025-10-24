import os
from sqlalchemy import create_engine, text


def main() -> None:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL environment variable is not set")

    engine = create_engine(database_url)
    with engine.begin() as conn:
        # Ensure required columns exist
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS employee_id VARCHAR(80) NULL"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS approved TINYINT(1) NOT NULL DEFAULT 0"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS username VARCHAR(80) NULL"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified TINYINT(1) NOT NULL DEFAULT 0"))
        conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS verification_code VARCHAR(16) NULL"))

        # Backfill username using employee_id where available
        conn.execute(text(
            "UPDATE users SET username = employee_id WHERE (username IS NULL OR username = '') AND employee_id IS NOT NULL AND employee_id <> ''"
        ))
        # Fallback to unique synthetic usernames
        conn.execute(text(
            "UPDATE users SET username = CONCAT('user', id) WHERE username IS NULL OR username = ''"
        ))

        # Add unique indexes
        conn.execute(text("ALTER TABLE users ADD UNIQUE INDEX IF NOT EXISTS uq_users_username (username)"))
        conn.execute(text("ALTER TABLE users ADD UNIQUE INDEX IF NOT EXISTS uq_users_employee_id (employee_id)"))

        # Enforce NOT NULL on username now that it's populated
        conn.execute(text("ALTER TABLE users MODIFY COLUMN username VARCHAR(80) NOT NULL"))

    print("✅ Aligned users table (columns ensured, usernames populated, constraints applied)")


if __name__ == "__main__":
    main()


