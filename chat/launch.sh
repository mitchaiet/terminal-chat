#!/bin/bash
DIR="$(dirname "$(readlink -f "$0")")"
exec "$DIR/chat.sh"
