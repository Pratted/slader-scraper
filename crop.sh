#!/bin/bash

file="$1"
convert $file -gravity East -chop 220x0 "$(dirname $file)tmp1$(basename $file)"
convert "$(dirname $file)tmp1$(basename $file)" -gravity South -chop 0x50 "$(dirname $file)tmp2$(basename $file)"
convert "$(dirname $file)tmp2$(basename $file)" -trim $file2

#rm tmp*$file
