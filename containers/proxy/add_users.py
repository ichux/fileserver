import argparse
import sqlite3
from contextlib import contextmanager

import bcrypt
from apps import DB_LOCATION, logger

parser = argparse.ArgumentParser(
    description="Manage users in the file server auth system."
)
parser.add_argument("username", help="The username of the user.")
parser.add_argument(
    "password",
    help="The password of the user (if adding a new user or changing password).",
)
parser.add_argument(
    "--enabled",
    choices=["True", "False"],
    help="Set the enabled status for the user (True/False).",
)
parser.add_argument(
    "--update-password",
    metavar="new_password",
    help="Update the password for the existing user.",
)

# Parse the arguments
args = parser.parse_args()


@contextmanager
def get_db_connection():
    conn = sqlite3.connect(DB_LOCATION)
    cursor_ = conn.cursor()
    try:
        yield cursor_
        conn.commit()
    except Exception as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


if args.update_password:
    # Update password for existing user
    try:
        hashed = bcrypt.hashpw(args.update_password.encode(), bcrypt.gensalt())
        with get_db_connection() as cursor:
            result = cursor.execute(
                "UPDATE users SET password_hash = ? WHERE username = ?",
                (hashed.decode(), args.username),
            )
            if cursor.rowcount == 0:
                logger.warning(
                    f"No user found with username '{args.username}' to update password."
                )
            else:
                logger.info(f"User '{args.username}' password updated successfully.")
    except Exception as e:
        logger.error(f"Failed to update password for '{args.username}': {e}")
elif args.enabled is not None:
    # Update enabled status for existing user
    try:
        enabled_status = True if args.enabled == "True" else False
        with get_db_connection() as cursor:
            result = cursor.execute(
                "UPDATE users SET enabled = ? WHERE username = ?",
                (enabled_status, args.username),
            )
            if cursor.rowcount == 0:
                logger.warning(
                    f"No user found with username '{args.username}' to update enabled status."
                )
            else:
                logger.info(
                    f"User '{args.username}' enabled status set to {args.enabled}."
                )
    except Exception as e:
        logger.error(f"Failed to update enabled status for '{args.username}': {e}")
else:
    # If no flags are set, treat as adding a new user
    try:
        hashed = bcrypt.hashpw(args.password.encode(), bcrypt.gensalt())
        with get_db_connection() as cursor:
            cursor.execute(
                (
                    "INSERT INTO users (added_on, updated_at, username, password_hash, enabled)"
                    " VALUES (CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, ?, ?, ?)"
                ),
                (args.username, hashed.decode(), True),
            )
        logger.info(
            f"User '{args.username}' inserted with hashed password successfully."
        )
    except sqlite3.IntegrityError:
        logger.error(f"User '{args.username}' already exists in the database.")
    except Exception as e:
        logger.error(f"Failed to insert user '{args.username}': {e}")
