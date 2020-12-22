#!/usr/bin/env python

"""Tests for `nodeeditor` package."""


import unittest

from node_editor.node_scene import Scene


class TestTemplate(unittest.TestCase):
    """Tests for `nodeeditor` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test if Scene got has_been_modified properly."""
        assert hasattr(Scene, 'has_been_modified')
