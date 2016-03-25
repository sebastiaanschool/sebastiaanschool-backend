#!/usr/bin/env bash
#
# Quickly check if all GET API's return something.
#
# Usage:
# - get-all.sh [hostname]     (default: 'http://localhost:8000')
#
FETCHER=$(which http)
if [ "$FETCHER" ]; then
    FETCHER="$FETCHER get"
else
    FETCHER="curl --verbose"
fi

ENDPOINT="http://localhost:8000"
if [ "$1" ]; then
    ENDPOINT="$1"
fi

set -e
for op in \
         "$ENDPOINT/api/agendaItems/" \
         "$ENDPOINT/api/bulletins/" \
         "$ENDPOINT/api/contactItems/" \
         "$ENDPOINT/api/newsLetters/" \
         "$ENDPOINT/api/timeline/"
do
    echo "GET $op"
    $FETCHER "$op"
    echo ''
done
