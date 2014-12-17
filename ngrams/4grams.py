import sys
import random
import mysql.connector as my

con_data={'user':'root','password':'agm','host':'127.0.0.1', \
'database':'ngrams','raise_on_warnings': True, 'autocommit':True, 'buffered':True}

con = my.connect(**con_data)
cur = con.cursor()

def sel1(p1):
    t = "select pal1, pal2, pal3, pal4 from es4 where pal1 = '%s' order by freq desc;" % p1
    cur.execute(t)
    fr = cur.fetchall()
    l = len(fr)
    if l > 1:
        sel = random.randrange(0,l-1)
        return fr[sel]
    else:
        try:
            return fr[0]
        except:
            return None

def sel1_2(p1):
    t = "select pal1, pal2, pal3, pal4 from es4 where pal2 = '%s' order by freq desc;" % p1
    cur.execute(t)
    fr = cur.fetchall()
    l = len(fr)
    if l > 1:
        sel = random.randrange(0,l-1)
        return fr[sel]
    else:
        try:
            return fr[0]
        except:
            return None
        

def sel2(p1, p2):
    t = "select pal1, pal2, pal3, pal4 from es4 where pal1 = '%s' and pal2 = '%s';" % (p1, p2)
    try:
        cur.execute(t)
    except:
        return None
    # print("sel2", t)
    fr = cur.fetchall()
    l = len(fr)
    if l > 1:
        sel = random.randrange(0,l-1)
        return fr[sel]
    else:
        try:
            return fr[0]
        except:
            return None

def sel3(p1, p2, p3):
    t = "select pal1, pal2, pal3, pal4 from es4 where pal1 = '%s' and pal2 = '%s' and pal3 = '%s';" % (p1, p2, p3)
    try:
        cur.execute(t)
    except:
        return None
    # print("sel3", t)
    fr = cur.fetchall()
    l = len(fr)
    if l > 1:
        sel = random.randrange(0,l-1)
        return fr[sel]
    else:
        try:
            return fr[0]
        except:
            return None

def decode(fr):
    p1 = fr[0].decode()
    p2 = fr[1].decode()
    p3 = fr[2].decode()
    p4 = fr[3].decode()
    retorno = []
    retorno.append(p1)  
    retorno.append(p2)
    retorno.append(p3)
    retorno.append(p4)
    return retorno

def main(clave, texto, rango, longo):
    fr = []
    count = 0
    fr = sel2('.', clave)
    if fr:
        fr = decode(fr)
        fr2 = [x for x in fr]
        fr2.pop(0)
        texto += " ".join(fr2)
        print(texto)
    if not fr:
        # print("nada para ", clave)
        c2 = 0
        while c2 < 5:
            fr = sel1(clave)
            if fr:
                fr = decode(fr)
                texto += " ".join(fr)
                # print(texto)
                break 
            else:
                print(("absolutamente nada para clave", clave))  
                sys.exit()         
    
    
    for a in range(rango):
        try:
            if len(texto) > longo:
                print(texto)
                sys.exit()
        except:
            print(("problemas", texto, longo))
        count = 0
        while count < 25:
            count +=1
            fr2 = sel3(fr[1], fr[2], fr[3])
            if fr2:
                fr = decode(fr2)
                texto += " " + fr[3]
                print(texto)
                continue
            else:
                count2 = 0
                while count2 < 15:
                    count2 +=1
                    fr2 = sel2(fr[2], fr[3])
                    if fr2:
                        fr = decode(fr2)
                        texto += " " + fr[2] + " " + fr[3]  
                        print(texto)
                        break
                    else:
                        while count2 < 23:
                            count2 +=1
                            fr2 = sel2(fr[1], fr[2])
                            if fr2:
                                fr = decode([x for x in fr2])
                                texto = texto[:texto.rfind(' ')+1]
                                texto += fr[2] + " " + fr[3]  
                                print(texto)
                                break
                            else:
                                # print("vamos a enmpezar de nuevo")
                                texto += ".\n"
                                main(clave, texto, rango-10, int)



if __name__ == '__main__':
    texto = ''
    longo = 1500
    clave = 'aldea'
    rango = 100
    main(clave, texto, rango, longo)
con.close()
