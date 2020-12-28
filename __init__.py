import os 
import json
from time import time
from threading import Lock
from .dataStoreExceptions import *


# Freshworks – Backend Assignment

#  fileName - dataStore.py
#  Requirement - To build a file-based key-value data store that supports the basic CRD (create, read, and delete) operations.

#  Assumptions - 

#  dataStore is exposed as a library to clients.
#  User or client application provides  TimeToLive property as optional parameter to 'create' method for each key

#  To import the main file as a library 
#  Usage -  from dataStore import dataStore as dataHandle 

#  dataStore can be initialized using an optional file path
#  If file path not provided, it will create itself in the current working directory.
#  defaultFile_path = os.getcwd()+'\\data_store.json'

class dataStore:

    def __init__(self, file_path = None):    # file path is optional to the client and requires json file type - {key : [ jsonObject, Time-To-Live, Timestamp ], }
        self.__file_path = file_path
        self.__lock = Lock()                  
        if self.__file_path : 
            if not os.access(self.__file_path, os.F_OK) : raise FileNotFound
            elif not os.access(self.__file_path, os.R_OK) : raise FileNotAccessible
            try:
                with open(self.__file_path): pass    
            except IOError: raise IOErrorOccurred    #throws user defined IO Exception if IOError occurred
        else:
            self.__file_path = os.getcwd() + '\\data_store.json'   # default file path is choosen as the current working directory
        
        with open(self.__file_path,'a+') : pass            # creation of JSON file if the default file path is choosen for the first time
        self.__file_size = os.stat(self.__file_path).st_size

    @staticmethod
    def __ValidateKey(self):                                        # private function
        if type(self.__key) is not str : raise InvalidKey                 # Check if Key is not string 
        elif len(self.__key) > 32 : raise KeyLengthExceeded               # Check if Key is exceeding 32 Chars


    # create() method creates new entry to json file, with key and value as required arguments
    # Each key supports setting a Time-To-Live property when it is created and it is optional

    # parameters: 
    # key_string <class 'str'> with maximum length of 32 characters, 
    # value <class 'jsonObject' > with maximum size of 16KB, 
    # timeToLive <class 'int'> as an integer defining the number of seconds the key must be retained in the data store

    def create(self, key, value, timeToLive = None):
        self.__key = key
        self.__value = value
        self.__timeToLive = timeToLive 
        self.__value_size = self.__value.__sizeof__()                   # get size of json Object value
        self.__ValidateKey                                              # Key is validated
        
        try : json.loads(self.__value)                                 # check if value is valid json object
        except json.JSONDecodeError: raise InvalidJSONobject           # throws user-defined exception along with exception for invalid JSON object

        with self.__lock:                                                       # locks the client process and provide thread safe
            self.__file_size = os.stat(self.__file_path).st_size                # to get dataStore file size
            if  self.__value_size > (1024 * 16) :                               # Check if JSON object size is exceeding 16KB (1 KiloByte = 1024 Bytes)
                raise ValueSizeExceeded
            elif (self.__value_size + self.__file_size)/1024 > (1024*1024) : 
                raise FileSizeExceeded

            if self.__timeToLive: 
                try : self.__timeToLive = int(self.__timeToLive)
                except : raise timeToLiveValueError
                
                if type(self.__timeToLive) is not int :pass
                self.__timeStamp = int(time())                                       # getting time of creation to manipulate Time to live property
            else : self.__timeStamp = None
            
            with open(self.__file_path,'r+') as self.__dataStoreFptr :                                  # adding key, value pair to dataStore                                     
                self.__data = {self.__key : (self.__value, self.__timeToLive, self.__timeStamp)}        # data is python object, dict() and Key has a tuple value (jsonObject, time to live attribute in seconds, time of creation of the KeyValue pair) making the key value immutable data           
                
                if self.__file_size is 0 :    
                    self.__dataStoreFptr.write(json.dumps(self.__data,indent = 4))                       # Serialize python object to a JSON formatted string and added to dataStore file
                else:
                    try : self.__data_store = json.load(self.__dataStoreFptr)
                    except json.JSONDecodeError:  raise InvalidJSONfile                         # Deserialize JSON file to a Python object, dict ()
                    
                    if self.__key in self.__data_store : raise DuplicateKey(self.__key)         # Check if Key already exists
                    else:
                        try : self.__data_store.update(self.__data)                              # data added to data_store object containing all data from json file
                        except AttributeError : raise InvalidJSONfile                            # throws exception if json file contains json array, valid json file requires to be a json object
                                
                        self.__dataStoreFptr.seek(0)                                # to reset the file pointer to position 0 
                        json.dump(self.__data_store, self.__dataStoreFptr)          # overwrite json file with data_store dict()



    # Reads the file, validates the key requested from client and 
    # returns the response from DataStore, if Time-To-Live condition satisfied 
    def read(self,key):
        with self.__lock:  
            self.__file_size = os.stat(self.__file_path).st_size                
            self.__key = key
            self.__ValidateKey
            if self.__file_size is 0 : raise EmptyFile                                  # Check if file is empty
            with open(self.__file_path, 'r') as self.__dataStoreFptr:
                try : self.__data_store = json.load(self.__dataStoreFptr)
                except json.JSONDecodeError:  raise InvalidJSONfile                          
                if self.__key not in self.__data_store : raise KeyNotExist(self.__key)  # Deserialize JSON file to a Python object, dict () and check Key existence
                else:
                    self.__data = self.__data_store[self.__key]
                    try : self.__isValidTimeToLive = ( int(time()) - self.__data[2] ) < self.__data[1]
                    except : raise InvalidJSONfile  
                    if self.__isValidTimeToLive : return json.dumps(self.__data[0])       # check if difference between current time and time of creation is less than time-to-Live value  
                    else: raise KeyExpired(self.__key)
                    
           
                
    # Deletes or removes JSONObject for given Key,if Valid key and Time-To-Live condition satisfied
    def delete(self,key):
        with self.__lock: 
            self.__file_size = os.stat(self.__file_path).st_size  
            self.__key = key
            self.__ValidateKey

            if self.__file_size is 0 : raise EmptyFile                                  # Check if file is empty
            with open(self.__file_path, 'r+') as self.__dataStoreFptr:                    
                try : self.__data_store = json.load(self.__dataStoreFptr)
                except json.JSONDecodeError:  raise InvalidJSONfile  

            if self.__key not in self.__data_store : raise KeyNotExist(self.__key)        # Deserialize JSON file to a Python object, dict () and check Key existence
            else:
                self.__data = self.__data_store[self.__key]
                try : self.__isValidTimeToLive = ( int(time()) - self.__data[2] ) < self.__data[1]
                except : raise InvalidJSONfile  
                if self.__isValidTimeToLive :          # check if difference between current time and time of creation is less than time-to-Live value
                    del self.__data_store[self.__key]
                    os.remove(self.__file_path)           # delete the file and recreate with new data store
                else: 
                    raise KeyExpired(self.__key)
                with open(self.__file_path, 'w') as self.__dataStoreFptr:
                    json.dump(self.__data_store,self.__dataStoreFptr)
                





                        



