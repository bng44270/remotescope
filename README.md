# remotescope

Requirement:  
* prescript.sh - [https://gist.github.com/bng44270/82f2e7b243966cf88bc9](https://gist.github.com/bng44270/82f2e7b243966cf88b9c)

Screencasting Client Setup:  
1. Run ```./prescript.sh remotescope.py```  
2. Run ```python remotescope```  
3. Type ```C``` to connect to a running server  
4. Type in the server address (and port number if necessary) and hit enter  
5. Type ```R``` to request a session from the server  
6. Type ```B``` to start your screencast  
7. Type ```S``` to stop your screencast  
8. Type ```E``` to disconnect from server  
  
Viewing Client Setup:  
1. Go to ```http://SERVERADDRESS:PORT/```  
2. The page you are directed to will be automatically populated with connected clients  
  
Server Setup:  
1. Verify the ```PORT=``` line of the ```remotescope.sh``` file contains your desired port number  
2. Run ```./remotescope.sh start```  
