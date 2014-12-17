from logpy import run, var, conde, Relation, facts
parent = Relation()
facts(parent, ('Homer', 'Lisa'),
      ('Homer', 'Bart'),
      ('Abe', 'Homer'))

x = var()
y = var()
print(run(1, x, parent(x, 'Bart')))
print(run(2, x, parent('Homer', x,)))
y = var()
print(run(1, x, parent(x, y),parent(y, 'Bart')))


def grandparent(x, z):
    y = var()
    return conde((parent(x,y), parent(y,z)))

print(run (1,x,grandparent(x, 'Bart')))


