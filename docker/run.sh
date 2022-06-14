SLOTH_HOME=/Users/breno/Documents/Workspace/sloth
echo ln -s /sloth /usr/local/lib/python3.10/site-packages/sloth
docker run --rm -it -v $SLOTH_HOME/test/checkin:/app -v $SLOTH_HOME/sloth:/sloth -p 8000:8000 auth bash