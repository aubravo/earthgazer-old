#!/bin/bash
user='alvaroubravo'
password='nApLdfGS6BBjFB9o'
urlsFile='./urls.txt'
queryFile='./queryresults.xml'
URL_='1234567https://scihub.copernicus.eu/dhus/search?q=footprint:"Intersects(POLYGON((-98.66855 19.05113, -98.58547 19.05113, -98.58547 18.98719,-98.66855 18.98719, -98.66855 19.05113)))" AND filename:S2A_*&"&rows=100"'

prepareURL () {
  local URL=$1
  URL=${URL:7:-1}
  URL=${URL//&quot;/%22}
  URL=${URL//&amp;/&}
  URL="${URL// /%20}"
  echo $URL
}

while [ ${#URL_} -gt 0 ]
do
  URL_=$(prepareURL "$URL_")
  wget --no-check-certificate --user=$user --password=$password \
  --output-document=$queryFile $URL_
  URL_=$(xpath -q -e '//link[@rel="next"]/@href' $queryFile)
  xpath -q -e '/feed/entry/str[@name="uuid"]/text()' $queryFile >> $urlsFile
  echo ${#URL_}
done

cat $urlsFile > copy.txt
sort $urlsFile complete.txt | uniq -u > copy2.txt
cat copy2.txt > $urlsFile

while read -r line
do
  wget --content-disposition --continue --user=$user --password=$password \
  --output-document=./tmp/$line \
  "https://scihub.copernicus.eu/dhus/odata/v1/Products('$line')/\$value"
  size=$(stat -c%s "./temp/$line")
  if (( size > 0 )); then
    echo $line >> complete.txt
    gsutil mv ./tmp/$line gs://gxiba-1-bucket/rawzips/$line
  fi
  sleep 300
done < $urlsFile
