#!/bin/bash
gsutil du -h gs://gxiba-1-bucket/ | \
awk '$1 == "0" { next } { print }' | \
awk '$3 ~ "/rawzips/." { print $3}' | \
sed 's/gs\:\/\/gxiba-1-bucket\/rawzips\///' > temp.txt

sort temp.txt complete.txt | uniq -u > temp2.txt
cat temp2.txt > temp.txt
rm temp2.txt

while read -r line
do
      gsutil cp gs://gxiba-1-bucket/rawzips/$line ./temp/$line
      unzip -q ./temp/$line -d ./temp/extracted_$line
      gsutil mv ./temp/extracted_$line gs://gxiba-1-bucket/extracted/$line
      rm ./temp/$line
      echo $line >> complete.txt
done < temp.txt
rm temp.txt
