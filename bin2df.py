import os
from transcad import zjcaliper3df

DEBUG_MODE = False

def convert(fname="BOSTON", furl=None, fout=None):

    ## design for cloud drive url: input from other place
    if furl != None: 
        fname  = os.path.basename(furl).split(".")[0]
        infname  = os.path.join( os.path.dirname(furl) , f'{fname}.bin')
        
        if fout == None:
            fout = f'output/{fname}.csv'
        else:
            fout = f'{fout}/{fname}.csv'

        csv = zjcaliper3df.dkbin_csv(filename=infname,
                                     outn=fout,
                                     is_debug=DEBUG_MODE)
        
    else:  ## input from internal input folder
        infname =  os.path.join("input", '%s.bin'%fname)
        csv = zjcaliper3df.dkbin_csv(filename=infname,
                                     outn=fout)
    print (csv)

if __name__ == '__main__':
    convert(fname = "HCM LinkFlow" )
    # url = r"J:\Shared drives\TMD_TSA\Model\platform\outputs\Base\_assignment\flows_pm_cvt.bin"
    # convert(furl = url )

    # for TOD in ["am",'md',"pm","nt"]:
    #     url = "J:\Shared drives\TMD_TSA\Model\platform\outputs\Base\_assignment\onoff_tw_%s.bin"%TOD
    #     convert(furl = url )
