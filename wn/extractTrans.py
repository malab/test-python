'''
Created on 15/10/2014

@author: aurelio
'''
import  mysql.connector as my


con_data = {'user':'root','password':'agm','host':'agm2.local', \
'database':'agiria','raise_on_warnings': True, 'autocommit':True, 'buffered':True}
con = my.connect(**con_data)
cur = con.cursor()
allPos = {}

def readPos(file):
    with open(file, 'rt') as f:
        lines = f.readlines()
        for line in lines:
            line = line[:-1]
            if line:
                datos = line.split(':')
                allPos[datos[0]] = datos[1]

                
def saveRecord(enPal, enPos, sense, esPal, esPos, offset):
    record = (enPal, enPos, sense, esPal, esPos, offset)
    t = "insert into senti_trans2 (en_word, en_pos, sense, es_word, en_pos, offset) \
    values (%s, %s, %s, %s, %s, %s)"
    print(t, record)
    try:
        pass
        #cur.execute(t, record)
    except my.Error as err:
        print("Error insertando: ", err, t)

def processRecords():
    t = "select distinct en_word, en_pos, sense from senti_trans limit 14900, 30;"
    cur2 = con.cursor()
    cur2.execute(t)
    allRec = cur2.fetchall()
    for rec in allRec:
        enPal = rec[0]
        enPos = rec[1]
        sense = rec[2]
        t = "select en_word, en_pos, sense, sp_word, sp_pos, offset from senti_trans where \
        en_word = %s and en_pos = %s and sense = %s;"
        cur1 = con.cursor()
        cur1.execute(t, (enPal, enPos, sense))
        allSame = cur1.fetchall()
        prevSense = ''
        numSense = 0
        eachSense = {}
        for cada in allSame:
            enSense = cada[2]
            if enSense not in eachSense: #we group the answers by sense
                eachSense[enSense] = []
            if enSense != prevSense:
                numSense +=1
                prevSense = enSense
            if numSense == 1:
                eachSense[enSense].append(cada)
            else:
                if enSense not in eachSense:
                    numSense +=1
                if enSense != prevSense:
                    numSense +=1
                    prevSense = enSense
                if numSense == prevSense:
                    eachSense[enSense].append(cada)                
            print(eachSense)
            esPal = cada[3]
            esPos = cada[4].strip()
            offset = cada[5]
            try:
                # print("processing: ", enPal, esPal, allPos[esPos], enPos,  allPos[esPos] == enPos)
                if allPos[esPos] == enPos: #if pos (adj, noun, verb, etc.) are equal in english and spanish 
                    saveRecord(enPal, enPos, sense, esPal, enPos, offset)
                elif esPos == '?' and enPos == 'v' and esPal[-2:] in ['ar', 'er', 'ir']: # assume it's a verb'
                    saveRecord(enPal, enPos, sense, esPal, enPos, offset)
            except KeyError as kr:
                pass
                # print("Key error: ", esPal, kr, esPos)
            except:
                print("Error before saving new record")

if __name__ == '__main__':
    readPos('data/sp_pos.txt')
    processRecords()