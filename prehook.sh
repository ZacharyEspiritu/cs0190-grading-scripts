#!/bin/bash

function with-code-import(){
  # the first argument is the path of the test file
  target="$1";
  # the second argument is the path to the code to test
  code="$2";
  # compute a relative path to the dependency
  code_rel="$(realpath --relative-to="$(dirname "$target")" "$code")";
  # replace the *-gdrive import with a file import
  perl -0777 -i.original -pe "s|my-gdrive\(\"[^\"]*\"\)|file\(\"$code_rel\"\)|gs" "$target"
  perl -0777 -i.original -pe "s|my-gdrive\('[^\"]*'\)|file\(\"$code_rel\"\)|gs" "$target"
  perl -0777 -i.original -pe "s|shared-gdrive\(\"[^\"]*\",\s*\"[^\"]*\"\)|file\(\"$code_rel\"\)|gs" "$target"
  rm "$target.original"
}

with-code-import "$(realpath tests.arr)" "$IMPL"
