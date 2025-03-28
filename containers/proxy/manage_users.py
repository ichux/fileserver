import argparse
import getpass

import bcrypt
from apps import SessionLocal, logger
from apps.models import User


def add_user(username: str, password: str, enabled: bool = True):
    with SessionLocal() as session:
        if session.query(User).filter(User.username == username).first():
            logger.info(f"User '{username}' already exists.")
            return

        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = User(username=username, password_hash=hashed, enabled=enabled)
        session.add(user)
        session.commit()

        logger.info(f"User '{username}' added successfully.")


def edit_user(username: str, password: str = None, enabled: bool = None):
    with SessionLocal() as session:
        user = session.query(User).filter(User.username == username).first()
        if not user:
            logger.info(f"User '{username}' does not exist.")
            return

        if password:
            hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
            user.password_hash = hashed

        if enabled is not None:
            user.enabled = enabled

        session.commit()
        logger.info(f"User '{username}' updated successfully.")


def main():
    parser = argparse.ArgumentParser(description="Manage users: add or edit a user.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand for adding a user
    add_parser = subparsers.add_parser("add", help="Add a new user")
    add_parser.add_argument("username", help="Username for the new user")
    add_parser.add_argument(
        "--password", help="Password (if not provided, you will be prompted)"
    )
    add_parser.add_argument(
        "--disabled", action="store_true", help="Set the user as disabled"
    )

    # Subcommand for editing a user
    edit_parser = subparsers.add_parser("edit", help="Edit an existing user")
    edit_parser.add_argument("username", help="Username of the user to edit")
    edit_parser.add_argument(
        "--password", help="New password (if not provided, you may be prompted)"
    )
    status_group = edit_parser.add_mutually_exclusive_group()
    status_group.add_argument("--enable", action="store_true", help="Enable the user")
    status_group.add_argument("--disable", action="store_true", help="Disable the user")

    args = parser.parse_args()

    if args.command == "add":
        password = args.password or getpass.getpass("Password: ")
        add_user(args.username, password, enabled=not args.disabled)
    elif args.command == "edit":
        password = args.password
        # Optionally prompt to change the password if not provided
        if password is None:
            change_pw = input("Change password? (y/n): ").strip().lower()
            if change_pw == "y":
                password = getpass.getpass("New password: ")

        enabled = None
        if args.enable:
            enabled = True
        elif args.disable:
            enabled = False

        edit_user(args.username, password, enabled)


if __name__ == "__main__":
    main()
