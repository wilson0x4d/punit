# SPDX-FileCopyrightText: © Shaun Wilson
# SPDX-License-Identifier: MIT

from punit.facts import fact

@fact
def unicodeShouldNotFailReportWriter() -> None:
    """
    Report writer was observed failing to encode the following unicode sequences.
    """
    print(u'\U0001f7e9')
