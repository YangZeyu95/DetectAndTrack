##############################################################
# Copyright (c) 2018-present, Facebook, Inc.
# All rights reserved.
#
# This source code is licensed under the license found in the
# LICENSE file in the root directory of this source tree.
##############################################################

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import contextlib
import multiprocessing
import logging
import Queue
import traceback

log = logging.getLogger(__name__)


class Coordinator(object):

    def __init__(self):
        self._event = multiprocessing.Event()

    def request_stop(self):
        log.debug('Coordinator stopping')
        self._event.set()

    def should_stop(self):
        return self._event.is_set()

    def wait_for_stop(self):
        return self._event.wait()

    @contextlib.contextmanager
    def stop_on_exception(self):
        try:
            yield
        except Exception:
            if not self.should_stop():
                traceback.print_exc()
                self.request_stop()


def coordinated_get(coordinator, queue):
    while not coordinator.should_stop():
        try:
            return queue.get(block=True, timeout=1.0)
        except Queue.Empty:  # multiprocessing also uses this
            continue
    raise Exception('Coordinator stopped during get()')


def coordinated_put(coordinator, queue, element):
    while not coordinator.should_stop():
        try:
            queue.put(element, block=True, timeout=1.0)
            return
        except Queue.Full:  # multiprocessing also uses this
            continue
    raise Exception('Coordinator stopped during put()')