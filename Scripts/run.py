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

import logging
import os
import subprocess
import sys

import config_reader as config
import pkg_resources
from bot import Logging, bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def validate_packages(file_path):
    """
    A function for checking the installed packages and installing the missing ones
    """

    def read_requirements(file_path):
        """
        A helper function for reading the requirements file
        """
        try:
            with open(file_path, "r") as file:
                return file.read().splitlines()
        except Exception as e:
            logger.error(f"An error occurred while trying to read {file_path}: {e}")
            return []

    def install_package(package_spec):
        """
        A function for checking if a package is installed and installing it if it isn't,
        also checking version requirements.
        """
        try:
            # Parse package name and version
            if "==" in package_spec:
                package_name, version = package_spec.split("==")
            else:
                package_name = package_spec
                version = None

            # Checking the package
            installed_version = None
            try:
                installed_version = pkg_resources.get_distribution(package_name).version
            except pkg_resources.DistributionNotFound:
                pass

            if version:
                if installed_version and installed_version == version:
                    pass
                else:
                    logger.info(
                        f"{package_name} version {version} not found or not matching. Installing..."
                    )
                    try:
                        subprocess.check_call(
                            [
                                sys.executable,
                                "-m",
                                "pip",
                                "install",
                                f"{package_name}=={version}",
                            ]
                        )
                        logger.info(
                            f"{package_name} version {version} has been installed."
                        )
                        return True
                    except subprocess.CalledProcessError as e:
                        logger.error(
                            f"Failed to install {package_name} version {version}: {e}"
                        )
                        return False
            else:
                if installed_version:
                    pass
                else:
                    logger.info(f"{package_name} not found. Installing...")
                    try:
                        subprocess.check_call(
                            [sys.executable, "-m", "pip", "install", package_name]
                        )
                        logger.info(f"{package_name} has been installed.")
                        return True
                    except subprocess.CalledProcessError as e:
                        logger.error(f"Failed to install {package_name}: {e}")
                        return False

        except Exception as e:
            logger.error(f"An error occurred while installing {package_spec}: {e}")
            return False

    packages = read_requirements(file_path)
    if not packages:
        return

    restart_needed = False

    for package_spec in packages:
        if install_package(package_spec):
            restart_needed = True  # Mark that we need to restart the script

    if restart_needed:
        logger.info("A package was installed. Restarting script...")
        os.execv(sys.executable, [sys.executable] + sys.argv)


if __name__ == "__main__":

    # Setup logger
    Logging.configure_logging()

    # Verifying packages
    try:
        requirements_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "requirements.txt",
        )
        validate_packages(requirements_path)
    except Exception as e:
        logger.error(f"An error occurred during package validation: {e}")
        sys.exit(1)

    # Verifying config and starting conditions
    try:
        config.validate(startup=True)
    except Exception as e:
        logger.error(f"An error occurred during config validation: {e}")
        sys.exit(1)

    # Getting rid of old logs
    try:
        Logging.purge_old_logs(config.Paths.logs_folder, 30 * 24 * 3600)
    except Exception as e:
        logger.error(f"An error occurred while purging old logs: {e}")
        sys.exit(1)

    # Starting the bot
    try:
        logging.info("Loading extensions...")
        bot.load_extensions_from("./ext", recursive=True)
        bot.load_extensions_from("./AutoMod")
        logging.info("Attempting to run bot")
        bot.run()
    except Exception as e:
        logger.error(f"An error occurred while running the bot: {e}")
        sys.exit(1)
