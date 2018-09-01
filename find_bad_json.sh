#!/bin/bash -p

for file in $1/result/*/results.json; do
  if ! (jq '.' $file > tmp) ; then
    echo "$file"
  fi
done

rm -f tmp
