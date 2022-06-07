import os
from transcad import zjcaliper3df


def convert(fname = "BOSTON" , furl = None):
    ## design for cloud drive url: input from other place
    if furl != None: 
        fname  = os.path.basename(furl).split(".")[0]
        infname  = os.path.join( os.path.dirname(furl) , '%s.bin'%fname)
        # print (infname)
        csv = zjcaliper3df.dkbin_csv(filename=infname,outn='output/%s.csv'%fname,debug_msgs=True)
    else:  ## input from internal input folder
        infname =  os.path.join("input", '%s.bin'%fname)
        csv = zjcaliper3df.dkbin_csv(filename=infname,outn='output/%s.csv'%fname)
    print (csv)

if __name__ == '__main__':
    convert(fname = "HCM LinkFlow" )
    # url = r"J:\Shared drives\TMD_TSA\Model\platform\outputs\Base\_assignment\flows_pm_cvt.bin"
    # convert(furl = url )

    # for TOD in ["am",'md',"pm","nt"]:
    #     url = "J:\Shared drives\TMD_TSA\Model\platform\outputs\Base\_assignment\onoff_tw_%s.bin"%TOD
    #     convert(furl = url )
