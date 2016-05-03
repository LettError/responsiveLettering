# -*- coding: utf-8 -*-

def validate(f):
    names = ['narrow-bold', 'wide-bold', 'narrow-thin', 'wide-thin']
    
    for n in names:
        g = f[n]
        print
        print g.name, len(g.contours)
        for c in g.contours:
            print g.name, len(c)
        

if __name__ == "__main__":
    f = CurrentFont()
    validate(f)