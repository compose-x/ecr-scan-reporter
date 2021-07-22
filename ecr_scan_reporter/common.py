#  -*- coding: utf-8 -*-
# SPDX-License-Identifier: MPL-2.0
# Copyright 2020-2021 John Mille<john@compose-x.io>

import itertools


def chunked_iterable(iterable, size):
    """
    Function to make chunks from iterable type
    `Source <https://alexwlchan.net/2018/12/iterating-in-fixed-size-chunks/>`__

    :param iterable:
    :param size:
    :return:
    """
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, size))
        if not chunk:
            break
        yield chunk
