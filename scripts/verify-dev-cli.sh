#!/bin/bash
# Dev mode test script

set -e

# Create temporary directory for CLI testing
TEMP_CONFIG_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_CONFIG_DIR"' EXIT INT TERM

echo "Testing experiment CLI commands..."
uv run wassden experiment --help > /dev/null 2>&1
uv run wassden experiment list-configs --config-path "$TEMP_CONFIG_DIR" > /dev/null 2>&1
uv run wassden experiment status --config-path "$TEMP_CONFIG_DIR" > /dev/null 2>&1

echo "✅ Dev functionality tests passed!"