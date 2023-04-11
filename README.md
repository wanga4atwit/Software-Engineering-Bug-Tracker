# Software-Engineering-Bug-Tracker
Bug Tracker for Software Engineering Project - Also known as BugTrackerNeo


## Features

- Handwritten Database
- Handmade connectivity using Socket Programming
- CLI Interface with multiple options
- You can close the client and open the client as many times as you want, the server will serve you the table where you left off

## Installation

Built EXE files are provided in the releases section. Download and unzip the folder wherever you want. Run serverAsync.exe first to run the backend. Then run clientAsync.exe. WAIT. The built version takes an excruciatingly long time to connect to the server compared to the standalone script. The built version is preloaded with a users table that contains one user "testUser" who's password is "password1234". (I know, so very unsafe. but this is for demo's sake). Once you log in further instructions will greet you so you can test functionality.

If you wish to build the code yourself...you don't. These can be run as scripts from the command line. Simply use "pip install -r requirements.txt" to install the required libraries, then run the files in the same order using a command line. The previously mentioned built EXE files were made using auto-py-to-exe for convenience but not required. 
