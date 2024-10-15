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

import config_reader as config
import vars


async def update_captcha_status():
    if config.Verification.disable_captcha:
        vars.captcha_enabled = False
        return

    if config.Verification.force_captcha:
        vars.captcha_enabled = True
        return

    if vars.raid:
        vars.captcha_enabled = True
        return

    vars.captcha_enabled = False
