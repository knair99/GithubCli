find . | grep -E "(__pycache__|.pytest_cache|\.pyc|\.pyo$)" | xargs rm -rf
rm -rf network_cache*
rm -rf *.txt
