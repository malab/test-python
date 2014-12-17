'''
Created on 2/11/2014

@author: aurelio
'''

class Connection(object):
    '''
    classdocs
    '''
    
    def connect(self):
        if self.tipo == 'mysql':
            import mysql.connector as my
            self.con = my.connect(**self.con_Data)
            self.error = my.Error
        elif self.tipo == 'mongo':
            from pymongo import MongoClient as mc
            client = mc(self.con_Data['server'], int(self.con_Data['port']))
            db = client[self.con_Data['database']]
            self.con = db[self.con_Data['collection']]
            
          
    def set_tipo(self, _tipo):
        self.tipo =  _tipo
    def get_tipo(self):
        if self.tipo:
            return self.tipo 
        else:
            return 'mysql'
    
    def set_db(self, _db):
        self.db = _db
    def get_db(self):
        if self.db:
            return self.db 
        else:
            return 'agiria'
        
    def set_host(self, _host):
        self.host = _host
    def get_host(self):
        if self.host:
            return self.host 
        else:
            return 'localhost'
        
    def set_user(self, _user):
        self.host = _user
    def get_user(self):
        if self.user:
            return self.user 
        else:
            return 'root'
        
    def set_pw(self, _pw):
        self.pw = _pw
    def get_pw(self):
        if self.pw:
            return self.pw 
        else:
            return ''


    def __init__(self, tipo):
        from xml.etree import ElementTree as et
        self.tipo = tipo
        et = et.parse('../con.xml')
        root = et.getroot()
        for child in root.iter(tipo):
            self.con_Data = {}
            for cada in child:
                d = cada.tag
                self.d = cada.text
                if cada.text == 'True' or cada.text == 'False':
                    self.con_Data[cada.tag] = bool(cada.text)
                else:
                    self.con_Data[cada.tag] = cada.text
        self.connect()
  
"""      
new = Connection('mongo')
con = new.con
topic = {"title" : 'Daroca'}
f = con.find_one(topic)
print(f['texto'])
"""
                

        