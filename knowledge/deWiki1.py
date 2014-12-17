'''
Created on 2/11/2014

@author: aurelio
'''
import sys
from conexion import Connection
from readDoc import *

def main():
    topic = 'Daroca'
    #topic = topic.capitalize()
    new = Connection('mongo')
    con = new.con
    topic = {"title" : topic}
    f = con.find_one(topic)
    if len(f['redirect']) > 10:
        redireccion = re.sub('#REDIRECT', '',f['redirect']).strip()
        topic = {"title" : redireccion}
        f = con.find_one(topic)
        if not f:
            print(topic, "\nno encontrado")
            sys.exit()
    elif not f or len(f['texto']) < 80:
        print("no encontrado")
        sys.exit() 
    doc = Document(f['texto'])
    num = 0
    for sent in doc.text.split("\n"):
        doc.addSentence(sent, num)
        num +=1
    doc.finishing()
    for sent in doc.sentences:
        print(sent.text)
    print("*"*100)
    for sent in doc.sentences:
        for pal in sent.words:
            print(pal.text, pal.lemma, pal.tag)

if __name__ == '__main__':
   main()