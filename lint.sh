#!/bin/sh
HAS_ERRORS=0

# Get files changed from master, filter for Python files, exclude patterns
for FILEPATH in $(git diff --name-only origin/master | grep "^app/.*\.py$"); do
    # Skip file if it was deleted
    [ ! -f "$FILEPATH" ] && continue

    # For debug purposes
    echo "$FILEPATH";

    # Run the ruff command with all arguments
    if ! "$@" "$FILEPATH"; then
        # Store exit code for error check later on
        HAS_ERRORS=1
    fi
done

exit $HAS_ERRORS
