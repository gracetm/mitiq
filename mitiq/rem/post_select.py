# Copyright (C) 2021 Unitary Fund
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from typing import Callable

from mitiq import Bitstring, MeasurementResult

import logging
from logging.handlers import RotatingFileHandler
import logging.config
import time

logging.config.fileConfig('python.conf')
logging.Formatter.converter = time.gmtime
handler = RotatingFileHandler('mitiq.log', encoding='utf-8', maxBytes=1000000, backupCount=1)
handler.setLevel(logging.INFO)
logger = logging.getLogger('mitiq.rem.post_select')
logger.addHandler(handler)

def post_select(
    result: MeasurementResult,
    selector: Callable[[Bitstring], bool],
    inverted: bool = False,
) -> MeasurementResult:
    """Returns only the bitstrings which satisfy the predicate in ``selector``.

    Args:
        result: List of bitstrings.
        selector: Predicate for which bitstrings to select. Examples:

            * ``selector = lambda bitstring: sum(bitstring) == k``
              - Select all bitstrings of Hamming weight ``k``.
            * ``selector = lambda bitstring: sum(bitstring) <= k``
              - Select all bitstrings of Hamming weight at most ``k``.
            * ``selector = lambda bitstring: bitstring[0] == 1``
              - Select all bitstrings such that the the first bit is 1.

        inverted: Invert the selector predicate so that bitstrings which obey
            ``selector(bitstring) == False`` are selected and returned.
    """
    # set up logging
    logger.info(f'\npost_select called with: \n'
                f'   result = {result}\n'
                f'   selector = {selector}\n'
                f'   inverted = {inverted}\n')

    results = MeasurementResult(
        [bits for bits in result.result if selector(bits) != inverted]
    )

    logger.info(f'\npost_select returning {results}\n\n')

    return results
