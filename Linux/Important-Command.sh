# check Running Port in Server
sudo lsof -i -P -n | grep LISTEN


#find file & folder in full syste,
find / --name "*regex*"

#kill Specific Port Using Script
kill -9 $(lsof -t -i:8000)
