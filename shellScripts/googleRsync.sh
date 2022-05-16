#!/bin/sh
/usr/bin/gsutil rsync -r -x '^(?!.*B[0-9]+\.TIF$).*' $1 gs://gxiba-1/LANDSAT/$2/