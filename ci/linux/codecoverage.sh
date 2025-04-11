# Any commands which fail will cause the shell script to exit immediately
set -e

# Set PRODUCT_SOURCE_DIR root directory
if [ "$PRODUCT_SOURCE_DIR" = "" ]; then
  RESTORE_DIRECTORY="$PWD"
  cd "$(dirname "$0")"
  cd ../..
  export PRODUCT_SOURCE_DIR="$PWD"
  echo "PRODUCT_SOURCE_DIR set to '$PRODUCT_SOURCE_DIR'."
  cd "$RESTORE_DIRECTORY"
  unset RESTORE_DIRECTORY
fi

# Change to product root directory
cd "$PRODUCT_SOURCE_DIR"

echo "Starting coverage unit tests..."
pytest -v --junitxml=unittests.xml --cov-report term --cov-report xml:coverage.xml --cov-report html:htmlcov --cov
echo done.
echo

echo "Generating coverage badge..."
coverage-badge -o coverage.svg
echo done.
echo
