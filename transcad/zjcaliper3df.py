

from . import caliper3_dataframes
import numpy as np 
import pandas as pd
import os



def dkbin_df(filename = "Amarillo Streets.bin", is_debug = False):

    '''
        how to read a Gisdk binary table into the dataframe and write a dataframe out to a Gisdk binary table
    '''
    # datatypes and row length in bytes
    dt_list, tcType_list, nBytesPerRow = caliper3_dataframes.read_dtypes(filename, is_debug)

    CODING = 'windows-1252'
    del_pattern = b'\x91\x8b\x4a\x5c\xbc\xdb\x4f\x14\x63\x23\x7f\x78\xa6\x95\x0d\x27'
    del_pattern = del_pattern[:min(nBytesPerRow, 16)]

    # TODO: assert might not be needed as there cannot be deleted records in tables with < 5 bytes per row
    assert nBytesPerRow >= 5, '''Cannot handle table with rows having  less than 5 bytes yet !!
                                Current row byte length {0}'''. format(nBytesPerRow)

    # ---Cleaning the file to remove the deleted records

    # reading file content as byte array
    with open(filename, mode='rb') as inFile:
        fileContent = inFile.read()
    file_array = bytearray(fileContent)

    # print (file_array)
    # removing the deleted records
    del_count = 0
    while file_array.find(del_pattern) > -1:
        pos = file_array.find(del_pattern)
        file_array = file_array[:pos] + file_array[pos + nBytesPerRow:]
        del_count += 1
    # print (file_array)
    if is_debug:
        print("+++ Infered byte length of row: {0}".format(nBytesPerRow))
        print("+++ Found {0} deleted rows".format(del_count))

    if is_debug:
        # writing the "corrected/cleaned" byte data
        if del_count > 0:
            with open(filename, "wb") as outFile:
                outFile.write(file_array)

    # ---Reading the cleaned file as np-array and then df
    dt = np.dtype(dt_list)
    data = np.fromfile(filename, dtype=dt)
    # print (dt_list)
    # print (dt)
    # print (data)
    df = pd.DataFrame.from_records(data)
    if is_debug:
        print("+++ Number of columns: ", len(dt_list))
        print("+++ Column data types infered: \n", dt_list)

    # ---Decoding the character fields
    char_columns = [item[0] for item in dt_list if 'S' in item[1]]
    for col in char_columns:
        df[col] = df[col].str.decode(CODING).str.strip()
        # --putting in None where values are ''
        df[col].mask(df[col] == '', None, inplace=True)

    df = caliper3_dataframes.read_na_values(df, dt_list)

    # ---handing date and time fields
    df = caliper3_dataframes.read_datetime(df, dt_list, tcType_list)
    return df



def dkbin_csv(filename = "Amarillo Streets.bin", outn = None, is_debug = False):

    '''
        how to read a Gisdk binary table into the dataframe and write a dataframe out to a Gisdk binary table
    '''
    # datatypes and row length in bytes
    if outn == None:
        base = os.path.basename(filename)
        outn = os.path.splitext(base)[0] +'.csv'
        midn = os.path.splitext(base)[0] +'_cleaned.bin'
    else:
        base = os.path.basename(filename)
        midn = os.path.splitext(base)[0] +'_cleaned.bin'
    print (filename)
    dt_list, tcType_list, nBytesPerRow = caliper3_dataframes.read_dtypes(filename, is_debug)

    CODING = 'windows-1252'
    del_pattern = b'\x91\x8b\x4a\x5c\xbc\xdb\x4f\x14\x63\x23\x7f\x78\xa6\x95\x0d\x27'
    del_pattern = del_pattern[:min(nBytesPerRow, 16)]

    # TODO: assert might not be needed as there cannot be deleted records in tables with < 5 bytes per row
    assert nBytesPerRow >= 5, '''Cannot handle table with rows having  less than 5 bytes yet !!
                                Current row byte length {0}'''. format(nBytesPerRow)

    # ---Cleaning the file to remove the deleted records

    # reading file content as byte array
    with open(filename, mode='rb') as inFile:
        fileContent = inFile.read()
    file_array = bytearray(fileContent)

    # print (file_array)
    # removing the deleted records
    del_count = 0
    while file_array.find(del_pattern) > -1:
        pos = file_array.find(del_pattern)
        file_array = file_array[:pos] + file_array[pos + nBytesPerRow:]
        del_count += 1
    # print (file_array)
    if is_debug:
        print("+++ Infered byte length of row: {0}".format(nBytesPerRow))
        print("+++ Found {0} deleted rows".format(del_count))

    # writing the "corrected/cleaned" byte data
    if is_debug:
        if del_count > 0:
            filename = midn
            with open(filename, "wb") as outFile:
                outFile.write(file_array)

    # ---Reading the cleaned file as np-array and then df
    dt = np.dtype(dt_list)
    # data = np.fromfile(filename, dtype=dt)
    data = np.frombuffer(file_array, dtype=dt)
    # print (dt_list)
    # print (dt)
    # print (data)
    df = pd.DataFrame.from_records(data)
    if is_debug:
        print("+++ Number of columns: ", len(dt_list))
        print("+++ Column data types infered: \n", dt_list)

    # ---Decoding the character fields
    char_columns = [item[0] for item in dt_list if 'S' in item[1]]
    for col in char_columns:
        df[col] = df[col].str.decode(CODING).str.strip()
        # --putting in None where values are ''
        df[col].mask(df[col] == '', None, inplace=True)

    df = caliper3_dataframes.read_na_values(df, dt_list)

    # ---handing date and time fields
    df = caliper3_dataframes.read_datetime(df, dt_list, tcType_list)
    
    df.to_csv(outn)
    return outn
    
if __name__ == '__main__':
    pass
