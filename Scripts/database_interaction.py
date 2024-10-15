# Copyright (C) 2024  Darkyl

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see https://www.gnu.org/licenses/.

import os
import shutil
import sqlite3
from datetime import datetime, timezone
from typing import Optional, Tuple

import config_reader as config

DB_PATH = os.path.join(config.Paths.data_folder, "Database", "users.db")


async def backup_database(db_path: str):
    try:

        from bot import logger

        logger.info("Attempting to back up database")

        from bot_utils import generate_id

        backup_path = os.path.join(
            os.path.dirname(DB_PATH), f"users_backup_{await generate_id()}"
        )

        # Copy the database file to a backup location
        shutil.copy2(db_path, backup_path)
        logger.info("Backup successful.")
    except Exception as e:
        logger.error(f"Error during backup: {e}")


def get_database_connection():
    try:
        return sqlite3.connect(DB_PATH)
    except FileNotFoundError as e:
        from bot import logger

        logger.error(f"Couldn't find path to database: {e}")
        return None
    except sqlite3.Error as e:
        from bot import logger

        logger.error(f"SQLite error occurred while trying to connect to database: {e}")
        return None
    except Exception as e:
        from bot import logger

        logger.error(
            f"An unexpected error occurred while trying to connect to database: {e}"
        )
        return None


class Users:
    def create_entry(
        user_id,
        message_count,
        xp,
        level,
        commands_used,
        reported,
        been_reported,
        nsfw_opt_out,
    ):
        nsfw_opt_out = int(nsfw_opt_out)
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    new_user = (
                        user_id,
                        message_count,
                        xp,
                        level,
                        commands_used,
                        reported,
                        been_reported,
                        nsfw_opt_out,
                    )
                    cursor.execute(
                        """
                        INSERT INTO users (id, msg_count, xp, level, cmds_used, reported, been_reported, nsfw_opt_out) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        new_user,
                    )
                    connection.commit()
                    return new_user
        except sqlite3.IntegrityError as e:
            from bot import logger

            logger.error(f"Integrity error while creating user entry: {e}")
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while creating user entry: {e}")
        except sqlite3.ProgrammingError as e:
            from bot import logger

            logger.error(f"Programming error while creating user entry: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while creating user entry: {e}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while creating new user entry: {e}"
            )
        return None

    def get_user_entry(user_id: int, values=None):
        """
        A function for getting a user entry from the database

        Args:
            user_id (int): The id of the user you want to get the entry for
            values (list of strings): Optional. A list of values you want to retrieve from the entry. If not specified, everything will be retrieved
                possible_values: (id, msg_count, xp, level, cmds_used, reported, been_reported, nsfw_opt_out)
        Returns:
            user_data (tuple): The database entry with the specified values
            None: If the user wasn't found or there was an error
        """
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    if values:
                        columns = ", ".join(values)
                        cursor.execute(
                            f"SELECT {columns} FROM users WHERE id = ?", (user_id,)
                        )
                    else:
                        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
                    user_data = cursor.fetchone()
                    return tuple(user_data) if user_data else None
        except sqlite3.OperationalError as error:
            from bot import logger

            logger.error(f"Operational error while reading user entry: {error}")
        except sqlite3.Error as error:
            from bot import logger

            logger.error(f"SQLite error while reading user entry: {error}")
        except Exception as e:
            from bot import logger

            logger.error(f"An unexpected error occurred while reading user entry: {e}")
        return None

    def update_user_entry(
        user_id: int,
        increment: bool = True,
        msg_count: int = 0,
        xp: int = 0,
        level: int = 0,
        cmds_used: int = 0,
        reported: int = 0,
        been_reported: int = 0,
        nsfw_opt_out: int = None,
    ) -> bool:
        """
        A function that modifies a user entry and creates one if it doesn't exist

        Args:
            user_id: The id of the user you want to modify the entry for
            increment: If True, values will be incremented instead of replaced
            msg_count: The number of messages the user has sent
            xp: The number of xp the user has
            level: The level of the user
            cmds_used: How many commands they have used
            reported: How many times the user reported
            been_reported: How many the user has been reported
            nsfw_opt_out: If they have opted out of nsfw (None for no change, 0 for no, 1 for yes)
        Returns:
            True: Success
            False: Error
        """
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()

                    if increment:
                        # Increment the values
                        sql = """
                            UPDATE users 
                            SET msg_count = msg_count + ?, xp = xp + ?, level = level + ?, cmds_used = cmds_used + ?, 
                                reported = reported + ?, been_reported = been_reported + ?
                        """
                        params = [
                            msg_count,
                            xp,
                            level,
                            cmds_used,
                            reported,
                            been_reported,
                        ]
                        if nsfw_opt_out is not None:
                            sql += ", nsfw_opt_out = ?"
                            params.append(nsfw_opt_out)
                        sql += " WHERE id = ?"
                        params.append(int(user_id))
                        cursor.execute(sql, params)
                    else:
                        # Replace the values
                        sql = """
                            UPDATE users 
                            SET msg_count = ?, xp = ?, level = ?, cmds_used = ?, reported = ?, been_reported = ?
                        """
                        params = [
                            msg_count,
                            xp,
                            level,
                            cmds_used,
                            reported,
                            been_reported,
                        ]
                        if nsfw_opt_out is not None:
                            sql += ", nsfw_opt_out = ?"
                            params.append(nsfw_opt_out)
                        sql += " WHERE id = ?"
                        params.append(int(user_id))
                        cursor.execute(sql, params)

                    # Check if any rows were affected
                    if cursor.rowcount == 0:
                        # No rows were updated, user does not exist, create user entry
                        Users.create_entry(
                            user_id,
                            msg_count,
                            xp,
                            level,
                            cmds_used,
                            reported,
                            been_reported,
                            nsfw_opt_out,
                        )

                    # Commit the transaction
                    connection.commit()
                    return True

        except sqlite3.IntegrityError as e:
            from bot import logger

            logger.error(f"Integrity error while updating user entry: {e}")
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while updating user entry: {e}")
        except sqlite3.ProgrammingError as e:
            from bot import logger

            logger.error(f"Programming error while updating user entry: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while updating user entry: {e}")
        except Exception as e:
            from bot import logger

            logger.error(f"An unexpected error occurred while updating user entry: {e}")
        return False

    def update_nsfw_status(user_id: int, nsfw_opt_out: bool) -> bool:
        nsfw_opt_out = int(nsfw_opt_out)

        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        """
                        UPDATE users 
                        SET nsfw_opt_out = ? 
                        WHERE id = ?
                    """,
                        (nsfw_opt_out, int(user_id)),
                    )
                    connection.commit()
                    return True
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(
                f"Operational error while updating nsfw status in the database: {e}"
            )
        except sqlite3.Error as e:
            from bot import logger

            logger.error(
                f"SQLite error while updating nsfw status in the database: {e}"
            )
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while updating nsfw status in the database: {e}"
            )
        return False

    def delete_user_entry(user_id: int) -> bool:
        """
        A function to delete a user entry from the database

        Args:
            user_id (int): The ID of the user you want to delete

        Returns:
            bool: True if the user was successfully deleted, False otherwise
        """
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                    connection.commit()
                    return cursor.rowcount > 0
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while deleting user entry: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while deleting user entry: {e}")
        except Exception as e:
            from bot import logger

            logger.error(f"An unexpected error occurred while deleting user entry: {e}")
        return False


class Messages:

    @staticmethod
    def create_message_entry(
        msg_id: int,
        content: str,
        channel_id: int,
        attachments: bool,
        author_id: int,
        created_at: str = None,  # Use ISO 8601 format for timestamps
        edited: int = 0,
    ) -> Optional[Tuple[int, str, int, int, int, int, str]]:
        """
        A function for creating a new message entry in the database

        Args:
            msg_id (int): The id of the message
            content (str): The content of the message
            channel_id (int): The id of the channel where the message was posted
            attachments (bool): Whether the message has attachments (True for yes, False for no)
            author_id (int): The id of the author of the message
            created_at (str): Timestamp for when the message was created (ISO 8601 format). Defaults to current time if not provided.
            edited (int): The version number of the message (default is 0, call create_message_edit_entry() to make edits)
        Returns:
            new_message (tuple): The new message entry if successfully created
            None: If there was an error
        """
        # Convert the boolean 'attachments' to an integer (0 or 1)
        attachments = int(attachments)
        # Set current timestamp if not provided
        created_at = created_at or datetime.now(timezone.utc).isoformat()

        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    new_message = (
                        msg_id,
                        content,
                        channel_id,
                        attachments,
                        author_id,
                        edited,
                        created_at,
                    )
                    cursor.execute(
                        """
                        INSERT INTO messages (msg_id, content, channel_id, attachments, author, edited, created_at) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        new_message,
                    )
                    connection.commit()
                    return new_message
        except sqlite3.IntegrityError as e:
            from bot import logger

            logger.error(f"Integrity error while creating message entry: {e}")
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while creating message entry: {e}")
        except sqlite3.ProgrammingError as e:
            from bot import logger

            logger.error(f"Programming error while creating message entry: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while creating message entry: {e}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while creating new message entry: {e}"
            )
        return None

    @staticmethod
    def create_message_edit_entry(
        msg_id: int,
        content: str,
        channel_id: int,
        attachments: bool,
        author_id: int,
    ):
        """
        A function for creating a new edited message entry in the database

        Args:
            msg_id (int): The id of the message
            content (str): The content of the message
            channel_id (int): The id of the channel where the message was posted
            attachments (bool): Whether the message has attachments (True for yes, False for no)
            author_id (int): The id of the author of the message
        Returns:
            new_message (tuple): The new message edit entry if successfully created
            None: If there was an error
        """
        # Convert the boolean 'attachments' to an integer (0 or 1)
        attachments = int(attachments)

        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    # Retrieve the current maximum 'edited' value for the given msg_id
                    cursor.execute(
                        "SELECT MAX(edited) FROM messages WHERE msg_id = ?", (msg_id,)
                    )
                    max_edited = cursor.fetchone()[0]
                    # If no edits exist, set edited to 0, otherwise increment
                    edited = 0 if max_edited is None else max_edited + 1

                    created_at = datetime.now(
                        timezone.utc
                    ).isoformat()  # Use current time for created_at

                    new_message = (
                        msg_id,
                        content,
                        channel_id,
                        attachments,
                        author_id,
                        edited,
                        created_at,
                    )
                    cursor.execute(
                        """
                        INSERT INTO messages (msg_id, content, channel_id, attachments, author, edited, created_at) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        new_message,
                    )
                    connection.commit()
                    return new_message
        except sqlite3.IntegrityError as e:
            from bot import logger

            logger.error(f"Integrity error while creating message edit entry: {e}")
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while creating message edit entry: {e}")
        except sqlite3.ProgrammingError as e:
            from bot import logger

            logger.error(f"Programming error while creating message edit entry: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while creating message edit entry: {e}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while creating new message edit entry: {e}"
            )
        return None

    @staticmethod
    def get_message_entry(msg_id: int):
        """
        A function for getting a message entry or entries from the database

        Args:
            msg_id (int): The id of the message you want to get the entry for
        Returns:
            message_data (dict or list of dicts): The database entry or entries of the message
            None: If the message wasn't found or there was an error
        """
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT * FROM messages WHERE msg_id = ? ORDER BY edited ASC",
                        (msg_id,),
                    )
                    rows = cursor.fetchall()
                    if rows:
                        # Define the column names based on the messages table structure
                        columns = [desc[0] for desc in cursor.description]
                        messages = [dict(zip(columns, row)) for row in rows]
                        # Return a list of dictionaries if there are multiple entries, else return a single dictionary
                        return messages if len(messages) > 1 else messages[0]
        except sqlite3.OperationalError as error:
            from bot import logger

            logger.error(f"Operational error while reading message entry: {error}")
        except sqlite3.Error as error:
            from bot import logger

            logger.error(f"SQLite error while reading message entry: {error}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while reading message entry: {e}"
            )
        return None

    @staticmethod
    def get_messages_by_author(author_id: int):
        """
        A function for getting all message entries from the database that share the same author

        Args:
            author_id (int): The id of the author whose messages you want to retrieve
        Returns:
            messages (list of dicts): A list of message entries by the author
            None: If no messages were found or there was an error
        """
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT * FROM messages WHERE author = ? ORDER BY msg_id, edited",
                        (author_id,),
                    )
                    rows = cursor.fetchall()
                    if rows:
                        # Define the column names based on the messages table structure
                        columns = [desc[0] for desc in cursor.description]
                        messages = [dict(zip(columns, row)) for row in rows]
                        return messages
        except sqlite3.OperationalError as error:
            from bot import logger

            logger.error(f"Operational error while reading messages by author: {error}")
        except sqlite3.Error as error:
            from bot import logger

            logger.error(f"SQLite error while reading messages by author: {error}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while reading messages by author: {e}"
            )
        return None

    @staticmethod
    def delete_message_entry(msg_id: int) -> bool:
        """
        A function to delete a message entry from the database

        Args:
            msg_id (int): The ID of the message you want to delete

        Returns:
            bool: True if the message was successfully deleted, False otherwise
        """
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM messages WHERE msg_id = ?", (msg_id,))
                    connection.commit()
                    return cursor.rowcount > 0
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while deleting message entry: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while deleting message entry: {e}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while deleting message entry: {e}"
            )
        return False

    @staticmethod
    def delete_messages_by_author(author_id: int) -> bool:
        """
        A function to delete all message entries from the database that share the same author

        Args:
            author_id (int): The ID of the author whose messages you want to delete

        Returns:
            bool: True if the messages were successfully deleted, False otherwise
        """
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "DELETE FROM messages WHERE author = ?", (author_id,)
                    )
                    connection.commit()
                    return cursor.rowcount > 0
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while deleting messages by author: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while deleting messages by author: {e}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while deleting messages by author: {e}"
            )
        return False


class Commands:

    @staticmethod
    def create_command_entry(
        user_id: int,
        command_name: str,
        options: str,
        used_at: str = None,
    ) -> bool:
        """
        A function for creating a new command entry in the database

        Args:
            user_id (int): The id of the user who ran the command
            command_name (str): The name of the command
            options (str): All of the provided options as a readable string
            used_at (str): Timestamp for when the command was used (ISO 8601 format). Defaults to current time if not provided.
        Returns:
            True: Success
            False: If there was an error
        """
        # Set current timestamp if not provided
        used_at = used_at or datetime.now(timezone.utc).isoformat()

        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    entry = (user_id, command_name, used_at, options)
                    cursor.execute(
                        """
                        INSERT INTO commands (user_id, cmd_name, used_at, options) 
                        VALUES (?, ?, ?, ?)
                        """,
                        entry,
                    )
                    connection.commit()
                    return True
        except sqlite3.IntegrityError as e:
            from bot import logger

            logger.error(f"Integrity error while creating command entry: {e}")
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while creating command entry: {e}")
        except sqlite3.ProgrammingError as e:
            from bot import logger

            logger.error(f"Programming error while creating command entry: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while creating command entry: {e}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while creating new command entry: {e}"
            )
        return False

    @staticmethod
    def get_commands_by_user(user_id: int):
        """
        A function for getting all command entries from the database that share the same user

        Args:
            user_id (int): The id of the user
        Returns:
            commands (list of dicts): A list of command entries by the user
            None: If no messages were found or there was an error
        """
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        "SELECT * FROM commands WHERE user_id = ?",
                        (user_id,),
                    )
                    rows = cursor.fetchall()
                    if rows:
                        # Define the column names based on the messages table structure
                        columns = [desc[0] for desc in cursor.description]
                        messages = [dict(zip(columns, row)) for row in rows]
                        return messages
        except sqlite3.OperationalError as error:
            from bot import logger

            logger.error(f"Operational error while reading commands of user: {error}")
        except sqlite3.Error as error:
            from bot import logger

            logger.error(f"SQLite error while reading commands of user: {error}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while reading commands of user: {e}"
            )
        return None

    @staticmethod
    def delete_commands_by_user(user_id: int) -> bool:
        """
        A function to delete all command entries from the database that share the same user

        Args:
            user_id (int): The ID of the user whose commands you want to delete

        Returns:
            bool: True if the commands were successfully deleted, False otherwise
        """
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute("DELETE FROM commands WHERE user_id = ?", (user_id,))
                    connection.commit()
                    return cursor.rowcount > 0
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while deleting commands of user: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while deleting commands of user: {e}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while deleting commands of user: {e}"
            )
        return False


class Reminders:
    """
    Status definition so I don't forget:
    0 = active
    1 = completed
    2 = canceled
    """

    @staticmethod
    def create_entry(
        id: str,
        user_id: int,
        reminder_time: str,
        message: str,
        channel_id: int,
        user_timezone: str,
        status: int = 0,
        dm: bool = True,
    ) -> bool:
        # used_at = datetime.now(timezone.utc).isoformat()

        dm = int(dm)

        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    entry = (
                        id,
                        user_id,
                        reminder_time,
                        message,
                        channel_id,
                        user_timezone,
                        status,
                        dm,
                    )

                    cursor.execute(
                        """
                        INSERT INTO reminders (id, user_id, reminder_time, message, channel_id, timezone, status, dm) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        entry,
                    )
                    connection.commit()
                    return True
        except sqlite3.IntegrityError as e:
            from bot import logger

            logger.error(f"Integrity error while creating reminder entry: {e}")
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while creating reminder entry: {e}")
        except sqlite3.ProgrammingError as e:
            from bot import logger

            logger.error(f"Programming error while creating reminder entry: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while creating reminder entry: {e}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while creating new reminder entry: {e}"
            )
        return False

    @staticmethod
    def read_reminders(
        user_id: int = None,
        channel_id: int = None,
        active: bool = None,
        past: bool = None,
    ):
        if active and past:
            raise ValueError(
                "You cannot read both active and past reminders at the same time."
            )

        query = "SELECT * FROM reminders WHERE 1=1"
        params = []

        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)

        if channel_id is not None:
            query += " AND channel_id = ?"
            params.append(channel_id)

        if active is not None:
            if active:
                query += " AND status = 0"  # 0 = active
            else:
                query += " AND status != 0"  # Not active

        if past is not None:
            now = datetime.utcnow().isoformat()
            if past:
                query += " AND reminder_time < ?"
            else:
                query += " AND reminder_time >= ?"
            params.append(now)

        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    if rows:
                        columns = [
                            column[0] for column in cursor.description
                        ]  # Get column names

                        # Convert rows to list of dictionaries
                        reminders = [dict(zip(columns, row)) for row in rows]
                        return reminders
                    else:
                        return []
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while reading reminders: {e}")
        except sqlite3.ProgrammingError as e:
            from bot import logger

            logger.error(f"Programming error while reading reminders: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while reading reminders: {e}")
        except Exception as e:
            from bot import logger

            logger.error(f"An unexpected error occurred while reading reminders: {e}")

        return None

    @staticmethod
    def update_reminder(
        reminder_id: str,
        new_time: str = None,
        new_message: str = None,
        new_status: int = None,
    ) -> bool:
        pass

    @staticmethod
    def complete_reminder(reminder_id: str) -> bool:
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        """
                        UPDATE reminders
                        SET status = 1
                        WHERE id = ?
                        """,
                        (reminder_id,),
                    )
                    connection.commit()
                    # Check if the update was successful
                    if cursor.rowcount == 0:
                        # No rows updated, which means the reminder_id was not found
                        return False
                    return True
        except sqlite3.IntegrityError as e:
            from bot import logger

            logger.error(f"Integrity error while updating reminder status: {e}")
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(f"Operational error while updating reminder status: {e}")
        except sqlite3.ProgrammingError as e:
            from bot import logger

            logger.error(f"Programming error while updating reminder status: {e}")
        except sqlite3.Error as e:
            from bot import logger

            logger.error(f"SQLite error while updating reminder status: {e}")
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while updating reminder status: {e}"
            )
        return False

    @staticmethod
    def cancel_reminder(reminder_id: str) -> bool:
        try:
            connection = get_database_connection()
            if connection:
                with connection:
                    cursor = connection.cursor()
                    cursor.execute(
                        """
                        UPDATE reminders
                        SET status = 2
                        WHERE id = ?
                        """,
                        (reminder_id,),
                    )
                    connection.commit()
                    # Check if the update was successful
                    if cursor.rowcount == 0:
                        # No rows updated, which means the reminder_id was not found
                        return False
                    return True
        except sqlite3.IntegrityError as e:
            from bot import logger

            logger.error(
                f"Integrity error while updating reminder status to canceled: {e}"
            )
        except sqlite3.OperationalError as e:
            from bot import logger

            logger.error(
                f"Operational error while updating reminder status to canceled: {e}"
            )
        except sqlite3.ProgrammingError as e:
            from bot import logger

            logger.error(
                f"Programming error while updating reminder status to canceled: {e}"
            )
        except sqlite3.Error as e:
            from bot import logger

            logger.error(
                f"SQLite error while updating reminder status to canceled: {e}"
            )
        except Exception as e:
            from bot import logger

            logger.error(
                f"An unexpected error occurred while updating reminder status to canceled: {e}"
            )
        return False
