#!/bin/bash

code_rel="$(realpath $2)"

sed -i "s@shared-gdrive(\"$1\".*)@file(\"$code_rel\")@g" $3
