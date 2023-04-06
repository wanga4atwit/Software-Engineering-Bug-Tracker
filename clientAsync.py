import socket
#mport tqdm
import os
import asyncio
import pandas as pd
import json
from datetime import date
import concurrent.futures

# device's IP address
SERVER_HOST = "localhost"
SERVER_PORT = 8000
# receive 4096 bytes each time
BUFFER_SIZE = 4096*4096
SEPARATOR = "<SEPARATOR>"
tempTable = None
#BIG BOILER PLATE CODE. Doesn't need anything the server doesn't already document. 
#To be edited when the serverside functions are done being implemented. 
#Testing each using main on a case by case basis for now. 
class Client: 
    def __init__(self, address):
        self.address=address

    async def connect(self):
        self.reader,self.writer=await asyncio.open_connection(*self.address)
        await self.handle_server(self.reader,self.writer)

    async def send_message(self,message):
        self.writer.write(message.encode())
        await self.writer.drain()
    async def sendPage(self,json):
        resp=(f'1<SEPARATOR>{json}<SEPARATOR>{None}')
        await self.send_message(resp)
    async def logInCLI(self):
        username=input("\nEnter your username\n")
        password=input("\nEnter your password\n")
        return (username,password)
    
    async def inputNewBugCLI(self):
          idNo=(-1)
          ticketTitle=input("Please provide a short name for the issue you are experiencing.")  
          ticketDescription=input("Please describe your issue in full detail.")
          ticketStatus="Unassigned"
          ticketDate=date.today()
          ticketDateResolved="Not Yet Resolved"
          AssignedTo='No One'
          newRow = pd.DataFrame([[idNo,ticketTitle,ticketDescription,ticketStatus,ticketDate,ticketDateResolved,AssignedTo]],columns=['ID','Title','Description','Status','Date Created','Date Resolved','Assigned To'])
          rowJson = newRow.to_json()
          await self.sendPage(rowJson)
    
    async def inputCLI(self):
        loop=asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            while True:
                print("Your choices are to: \n")
                print("Type 1 to file a new bug.")
                print("Type 2 to edit an existing bug")
                print("Type 3 to delete an existing bug")
                print("Type 4 to close the program.")
                print("Type 5 to see the current page.")
                choice=await loop.run_in_executor(pool,input,"\nMake your choice...\n")
                if(int(choice)==1):
                    await self.inputNewBugCLI()
                elif(int(choice)==5):
                    print(self.tempTable)
                else:
                    break
        
    async def handle_server(self, reader, writer):
        try:
            loginDetails = await self.logInCLI()
            await self.send_message(f'0<SEPARATOR>{loginDetails[0]}<SEPARATOR>{loginDetails[1]}')
            userInputTask=asyncio.create_task(self.inputCLI())
            while True:
                data=await reader.read(BUFFER_SIZE)
                receivedData=data.decode()
                dataParts=receivedData.split(SEPARATOR)
                if(len(dataParts)==2):
                    header = dataParts[0]
                    data1 = dataParts[1]
                    if(header=='30'):
                        jsonTable=json.loads(data1)
                        self.tempTable=pd.read_json(json.dumps(jsonTable))
                        print(tempTable)
                    if(header=='20'):
                        print(data1)
                    if(header=='21'):
                        print("\nLog-In Failure, please try again.\n")
                        loginDetails = await self.logInCLI()
                        await self.send_message(f'0<SEPARATOR>{loginDetails[0]}<SEPARATOR>{loginDetails[1]}')
                else:
                    header=dataParts[0]
                    data1='No Data'                   
                if data:
                    print(f'Recieved header: {header}, with data slot 1: {data1}')
                else:
                    print('Client disconnected either because it was manually shut down or an internal error.')
                    break
        except ConnectionError:
            print('An Error has occured between the Server and Client')
        finally:
            await self.close()

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

async def main():
    client=Client((SERVER_HOST,SERVER_PORT))
    clientControllerTask=asyncio.create_task(client.connect())
    await asyncio.gather(clientControllerTask)
    #await client.connect()
    #await client.close()
if __name__ == '__main__':
    asyncio.run(main())

