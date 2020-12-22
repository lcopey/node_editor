#!/usr/bin/env python

"""Tests for `nodeeditor` package."""


import unittest

from node_editor.node_editor_widget import NodeEditorWidget


class TestTemplate(unittest.TestCase):
    """Tests for `nodeeditor` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_nodeeditorwidget(self):
        """Test if Scene got has_been_modified properly."""
        NodeEditorWidget()
        assert hasattr(NodeEditorWidget, 'has_been_modified')
