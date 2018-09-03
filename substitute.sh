#!/bin/bash

sed -i -e "s/shared-gdrive\(\"$1\".*\)/file\(\"$2\"\)/g" $3