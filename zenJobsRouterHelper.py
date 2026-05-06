#!/usr/bin/env python
"""
zenJobsRouterHelper - Backwards compatibility shim.

This module exists solely for backwards compatibility with code that imported
from zenJobsRouterHelper before zenApiJobsRouterHelper was introduced.
All examples and new code should import from zenApiJobsRouterHelper directly.
No functions are defined here intentionally - they live in zenApiJobsRouterHelper
to avoid maintaining duplicate implementations that could drift out of sync.
"""
from __future__ import absolute_import
from zenApiJobsRouterHelper import checkJobStatus, watchStatus  # noqa: F401
