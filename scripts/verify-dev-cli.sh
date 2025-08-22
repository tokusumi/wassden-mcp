#!/bin/bash
# Dev mode test script

set -e

echo "Testing experiment CLI commands..."
uv run wassden experiment --help > /dev/null 2>&1
uv run wassden experiment list-configs > /dev/null 2>&1
uv run wassden experiment status > /dev/null 2>&1

echo "✅ Dev functionality tests passed!"