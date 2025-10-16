#!/usr/bin/env bash
export DJANGO_SETTINGS_MODULE=config.settings
coverage run --source=lms,users manage.py test -v 2
coverage report -m > coverage_report.txt
coverage xml -o coverage.xml
coverage html -d htmlcov
echo "Coverage reports generated: coverage_report.txt, coverage.xml, htmlcov/"