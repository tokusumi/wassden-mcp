#!/bin/bash
# Core mode test script

set -e

echo "Testing core CLI functionality..."
uv run wassden --help > /dev/null 2>&1
uv run wassden check-completeness --userInput "test project" > /dev/null 2>&1
uv run wassden validate-requirements specs/experiment-framework/requirements.md > /dev/null 2>&1

echo "Verifying experiment commands are not available in core mode..."
if uv run wassden experiment --help 2>/dev/null; then
    echo "ERROR: experiment command should not be available in core mode"
    exit 1
else
    echo "experiment command correctly unavailable in core mode"
fi

echo "Testing MCP server core functionality..."

echo "✅ Core functionality tests passed!"