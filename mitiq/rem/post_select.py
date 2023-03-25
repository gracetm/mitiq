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

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
handler = RotatingFileHandler('mitiq.log', maxBytes=1000000, backupCount=1)
handler.setLevel(logging.INFO)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s'))
logger = logging.getLogger('mitiq.rem.post_select')
logger.addHandler(handler)
logger.setLevel(logging.INFO)

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
    logger.info(f'post_select called with: \n')
    logger.info(f'   result = {result}\n')
    logger.info(f'   selector = {selector}\n')
    logger.info(f'   inverted = {inverted}\n')

    results = MeasurementResult(
        [bits for bits in result.result if selector(bits) != inverted]
    )

    logger.info(f'post_select returning {results}\n\n')

    return results
