#!/bin/bash -p

jq --slurp '.' $1/result/*/results.json > $1/result/results.json
