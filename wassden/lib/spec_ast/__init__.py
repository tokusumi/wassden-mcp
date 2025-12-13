"""Spec AST module for structured document parsing and validation.

This module provides an AST-based approach to parsing and validating specification documents.
It replaces the text-scanning validation system with a structured object model.
"""

from wassden.lib.spec_ast.blocks import (
    BlockType,
    DocumentBlock,
    ListItemBlock,
    RequirementBlock,
    SectionBlock,
    SpecBlock,
    TaskBlock,
)

__all__ = [
    "BlockType",
    "DocumentBlock",
    "ListItemBlock",
    "RequirementBlock",
    "SectionBlock",
    "SpecBlock",
    "TaskBlock",
]
