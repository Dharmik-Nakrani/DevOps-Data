#!/bin/bash

mkdir -p ~/dumps
mkdir -p ~/scripts

filename=$(date +'%d-%m-%Y')
echo "Backing up databases to ${filename}.sql"

# for local server database
mysqldump -u<root> -p<pass123> --databases <database> > ~/dumps/${filename}.sql

# For deffrent server database (eg.RDS)
mysqldump -h <hostname> -u<root> -p<pass123> --databases <database> > ~/dumps/${filename}.sql


-------------------------------------------------
#!/bin/bash

filename=$(date -d "-7 days" +'%d-%m-%Y')
echo "Removing old backup: ${filename}.sql"

# Remove the old backup file
rm /home/ubuntu/dumps/${filename}.sql

-------------------------------------------------
