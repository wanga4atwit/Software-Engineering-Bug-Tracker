import socket
#mport tqdm
import os
import asyncio
import pandas as pd
import random
#Above here is all and any imports

#IP Address of the server
SERVER_HOST = "0.0.0.0"
#Port of the server
SERVER_PORT = 8000
# receive 4096 bytes each time
BUFFER_SIZE = 4096
#I was going to use this seperator and then forgot and declared a new one, whatever.
SEPARATOR = "<SEPARATOR>"
#User-login table. Probably a better way to generate these but for now they are what they are.
#Should replace this later if I have the time.
userTable=pd.DataFrame(columns=['username','password','tableID'])
idNo=random.randint(0,99999)
testuser=pd.DataFrame([['testUser','password1234',idNo]],columns=['username','password','tableID'])
userTable = pd.concat([userTable,testuser])
#TLDR, create a table with the columns for a user, make an id for their table, make the user, add the user.

#Server class
class Server: 
    #Init function. takes address and maps self.
    def __init__(self,address):
        self.address = address;
        print('Initialized') 
    #Here the server starts up
    async def start(self):
        #I printed the address for debugging
        print(self.address)
        #the server starts using asyncIO, and maps the function and address as parameters.
        self.server = await asyncio.start_server(self.handle_client,*self.address)
        #I added this to fix connection issues, seems to do the trick. Thanks StackOverflow!
        async with self.server:
            await self.server.serve_forever()
        #This print never happens because serve_forever never ends until the server does. Whatever.
        print('server start(self) completed')
    #function for the loginProcess, takes self,user,passwd. Not fully implemented yet but the skeleton is here.
    #After a log in I need to set some variables for the current session, send a message, etc
    #For user or password errors I need to send a message to the client. FML.
    #In here, I check if the username sent is in the table, and if it is, if the password matches.
    #Yeah plain-text is unsafe but I have 14 days to complete this junk so what gives.
    async def loginProcess(self,user,passwd):
        if(userTable['username'].isin([user]).any()==True):
            if((userTable.loc[userTable['username']==user,'password'].item())==passwd):
                print("Username and password confirmed, logging in the user")
            else:
                print("Password Error")
        else:
            print("Username Error")
    #All the juice happens in here. This is the handler/controller
    #We catch it all in a try so that if I fuck up it throws an error. So far so good.
    async def handle_client(self,reader,writer):
        try:
            while True:
                #read the data into the buffer.
                data = await reader.read(BUFFER_SIZE)
                #decode the message
                message = data.decode()
                #Split the data, messages to our API will have to be compliant to this. I'll document it later.
                dataParts = message.split(',')
                #Header definition list
                #0=Login
                #1=Row Add
                #2=Row Edit
                #3=Row Delete

                #if the message is 3 parted (Correctly formed), proceed, if not, then the Client will disconnect.
                #Clients should pad the additonal data slots with 0.
                if(len(dataParts)==3):
                    header = dataParts[0]
                    data1 = dataParts[1]
                    data2 = dataParts[2]
                    #if the header implies a log-in request
                    if(header=='0'):
                        print('Initiating Log In Process')
                        #duplication for my sanity, whatever.
                        username=data1
                        password=data2
                        #do the login process documented above. Ideally more stuff happens, not fully implemented.
                        await self.loginProcess(username,password)
                else:
                    #else if, the header is malformed or single messaged, for us it defaults to disconnect. But padding Data 1 and 2 stops crashes.
                    header=dataParts[0]
                    data1='No Data'
                    data2='No Data'
                if message:
                    #Debug message, likely to dissapear in the future.
                    print(f'Recieved header: {header}, with data slot 1: {data1} and data slot 2: {data2}')
                    #Sends the data right back to the client. Debugging for me.
                    writer.write(data)
                    #Wait for the writer to finish
                    await writer.drain()
                else:
                    #if the message was that malformed boi above, the client likely disconnected. Quit the handler.
                    print('Client disconnected')
                    break
        except ConnectionResetError:
            print('Client connection reset')
        finally:
            writer.close()
        #close our writer if the connection dropped, no need for it anymore.
    #Function to neatly close the server. I haven't implemented this yet anywhere but its here when we need it.
    async def stop(self):
        print('Server Stopping')
        self.server.close()
        await self.server.wait_closed()
    



#main function kicks this shit off. 
async def main():
    #create our server with the provided server and port
    server = Server((SERVER_HOST,SERVER_PORT))
    print('Server Starting')
    #run the start function.
    await server.start()
    print('Server Started.')

if __name__ == '__main__':
    asyncio.run(main())

    