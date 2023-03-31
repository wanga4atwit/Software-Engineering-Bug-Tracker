import socket
#mport tqdm
import os
import asyncio
import pandas as pd
import json

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
        
    async def handle_server(self, reader, writer):
        try:
            await self.send_message('0<SEPARATOR>testUser<SEPARATOR>password1234')
            while True:
                data=await reader.read(BUFFER_SIZE)
                receivedData=data.decode()
                dataParts=receivedData.split(SEPARATOR)
                if(len(dataParts)==2):
                    header = dataParts[0]
                    data1 = dataParts[1]
                    if(header=='30'):
                        jsonTable=json.loads(data1)
                        tempTable=pd.read_json(json.dumps(jsonTable))
                        print(tempTable)
                    if(header=='20'):
                        print(data1)
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
    await client.connect()
    #await client.close()
if __name__ == '__main__':
    asyncio.run(main())

