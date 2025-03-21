#!/bin/bash
cd src/

echo "Extracting messages for Python code..."

# Some constants are generated and can be ignored.
python manage.py makemessages \
--all \
--ignore="test_*" \
--ignore="openforms/api/tests/error_views.py" \
--ignore="openforms/prefill/contrib/haalcentraal/constants.py" \
--ignore="openforms/prefill/contrib/kvk/constants.py" \
--ignore="openforms/registrations/constants.py"

cd ..

echo "Extracting messages for Javascript code..."
./bin/makemessages_js.sh

echo "Make sure to run './bin/compilemessages_js.sh' when done translating."
echo "Done."
