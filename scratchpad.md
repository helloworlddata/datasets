


Pipe a bunch of files into one gzip:

~~~sh
echo "New York Police Stop and Frisk data, packaged by Dan Nguyen on 2016-06-06, for https://github.com/dataofnote" > /tmp/README.md

csvstack data/wrangled/stops-and-frisks--{2013,2014,2015}.csv \
  > /tmp/nypd-stop-question-and-frisk.packaged.2013.to.2015.csv

tar -cvzf /tmp/nypd-stop-question-and-frisk.packaged.2013.to.2015.csv.tar.gz \
  /tmp/README.md \
  /tmp/nypd-stop-question-and-frisk.packaged.2013.to.2015.csv

aws s3 cp /tmp/nypd-stop-question-and-frisk.packaged.2013.to.2015.csv.tar.gz \
  s3://packages.dataofnote.com/nypd-stop-question-and-frisk/2013.to.2015.csv.tar.gz --acl public-read
~~~
