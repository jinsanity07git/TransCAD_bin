import os
from transcad import zjcaliper3df


def convert(fname = "BOSTON" ):
    infname =  os.path.join("input", '%s.bin'%fname)
    csv = zjcaliper3df.dkbin_csv(filename=infname,outn='output/%s.csv'%fname)
    print (csv)

if __name__ == '__main__':
    convert(fname = "HCM LinkFlow" )