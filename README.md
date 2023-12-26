# A simple file transfer program using Python socket
## Getting started
First, you need to run the server:
### `python newserver.py`
After that, run your first client and enter PORT 9000
### `python newclient.py`
Run your second client and enter PORT 9001 (NOTE: Use another cmd)
### `python newclient.py`
Now, let the first client push a file
### `push a.png`
And the second client can get the list of all client who owns that file
### `get a.png`
In this case, there is only 1 client owns that file, simply fetch from that client
### `fetch 0`



