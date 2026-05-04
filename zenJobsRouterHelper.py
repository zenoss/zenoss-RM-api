#!/usr/bin/env python
"""
zenJobsRouterHelper - Backwards compatibility shim.
Import zenApiJobsRouterHelper for new code.
Compatible with Python 2.7 and Python 3.6+
"""
from __future__ import absolute_import
from zenApiJobsRouterHelper import checkJobStatus, watchStatus  # noqa: F401
