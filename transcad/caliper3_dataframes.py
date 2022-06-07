import imp
import sys
import numpy as np
import pandas as pd
import csv
import os 
# ======================================================================================================


def read_dtypes(fname, debug_msgs=False):
    '''
        reads d_type of columns from dcb file
    '''
    dcb_fname = fname.split('.bin')[0] + '.DCB'
    if os.path.exists(dcb_fname):
        pass
    else:
        dcb_fname = fname.split('.bin')[0] + '.dcb'

    assert os.path.exists(dcb_fname), "dcb file not exist"

    # --map from transCAD to numpy
    read_type_map = {'C': 'S', 'R': 'f', 'S': 'i', 'F': 'f', 'I': 'i', 'Date': 'i', 'Time': 'i'}
    field_list = []

    with open(dcb_fname) as dcb_file:
        # looping over the lines
        for aLine in dcb_file:
            aLine = aLine.strip()
            aLine = aLine.split(',')
            # ---the field definitions have 13 elements
            # ---the field definitions have 10 elements: for gisdk macro export
            # TODO: (i) currently split all commnas; to ignore ones in quotes, (ii) date, time, date and time is to be interpreted
            if len(aLine) >= 10:
                field_dict = {}
                field_dict['name'] = aLine[0].strip('\'"')
                # ---intepreting
                type_name, type_size = aLine[1], aLine[3]
                if type_name == 'S' and type_size == '1':
                    field_dict['spec'] = 'u1'
                elif type_name == "DateTime":
                    pass
                else:
                    try:
                        npType = read_type_map.get(type_name)
                    except:
                        raise TypeError("The TC type {0} is not supported".format(type_name))
                    
                    field_dict['spec'] = npType + type_size

                field_dict['tcType'] = type_name
                
                #---DateTime is handled seperately by creating two columns
                if type_name == 'DateTime':
                    field_list.append({'name' : field_dict['name'] + "_date", "spec" : 'i4', 'tcType': type_name})
                    field_list.append({'name' : field_dict['name'] + "_time", "spec" : 'i4', 'tcType': type_name})
                else:
                    field_list.append(field_dict)

            if len(aLine) == 1:
                try:
                    aLine = aLine[0].split()
                    row_byte_len = int(aLine[0])
                    if aLine[1] == 'binary':
                        raise TypeError("The input binary file appears not to be a FFB file")
                except:
                    pass

    if debug_msgs:
        print ("length of field definitions: %s" %len(aLine))
        print('field_infer_list: ')
        for field_item in field_list:
            print(field_item)

    assert len(field_list) > 0, "There are no valid field definitions in {0}".format(dcb_fname)
    dt_list  = [(item['name'], item['spec']) for item in field_list]
    tcType_list = [(item['name'], item['tcType']) for item in field_list]
    return dt_list, tcType_list, row_byte_len

# ======================================================================================================


def read_na_values(df, dt_list):
    '''
        sets the na values of char, int and float columns in bin table
        to be compatible with pandas dataframe
    '''
    # ---The "values" of NA
    VSHORT_MISS = 255
    SHORT_MISS = -32767
    LONG_MISS = -2147483647
    FLT_MISS = -3.4028234663852886e+38
    DBL_MISS = -1.7976931348623158e+308

    # ---NA is coded and sepearately for each dtype. We set them to np.nan
    # --Integet columns
    int_columns = [item for item in dt_list if any(i in item[1] for i in ['i', 'u'])]
    # Putting in np.nan where values are min limits
    for col, a_dtype in int_columns:
        # --Changing to pd Int to have NA in integer columns
        pd_dtype = 'Int32'
        if 'u1' in a_dtype:
            # pd_dtype = 'Int8' # TODO: Make this compatible with unsign integer it is
            min_limit = VSHORT_MISS
        elif '2' in a_dtype:
            pd_type = 'Int16'
            min_limit = SHORT_MISS
        elif '4' in a_dtype:
            pd_dtype = 'Int32'
            min_limit = LONG_MISS
        else:
            raise TypeError("Unknown Integer Type {0} for column {1}".format(a_dtype, col))

        df[col] = df[col].astype(dtype=pd_dtype)
        df[col] = df[col].mask(df[col] == min_limit, other=np.nan)

    # ---Floating point columns
    float_columns = [item for item in dt_list if 'f' in item[1]]
    # Putting in np.nan where values are min limits
    for col, a_dtype in float_columns:
        if '4' in a_dtype:
            min_limit = FLT_MISS
        elif '8' in a_dtype:
            min_limit = DBL_MISS
        else:
            raise TypeError("Unknown float Type: {0}".format(a_dtype))

        df[col].mask(df[col] == min_limit, np.nan, inplace=True)

    return df

# ======================================================================================================

def read_datetime(df, dt_list, tcType_list):
    '''
        read_datetime(): converts the date, time, and datatime objects to pandas datetime64 type
    '''
    date_cols = [item[0] for item in tcType_list if item[1] == 'Date']
    time_cols = [item[0] for item in tcType_list if item[1] == 'Time']
    dtime_cols = list(set( [item[0][:-5] for item in tcType_list if item[1] == 'DateTime'] )) # getting rid of '_date' and '_time'

    #--converting date cols inplace
    for col_name in date_cols:
        df[col_name] = pd.to_datetime(df[col_name].astype('str'), errors = 'coerce')

    #---converting time cols inplace
    for col_name in time_cols:    
        df[col_name] = pd.to_datetime(df[col_name], unit = 'ms')

    #---converting dtime cols and droping the old cols
    for col_name in dtime_cols:
        df[col_name + '_date'] = pd.to_datetime(df[col_name + '_date'].astype('str'),  errors = 'coerce')
        df[col_name + '_time'] = pd.to_datetime(df[col_name + '_time'], unit = 'ms').dt.time
        df[col_name] = pd.to_datetime(df[col_name + '_date'].astype('str') + ' ' + df[col_name + '_time'].astype('str'),  errors = 'coerce')
        df.drop(columns = [col_name + '_date', col_name + '_time'], inplace = True)


    return df

#========================================================================================================

def write_dcb_file(outFilename, df, col_dtypes, dt_cols, nBytesPerRow):
    '''
        writes dcb file for based on col_dtypes
        col_dtypes: a dict of col_name: d_type ('intxx', 'floatYY', 'SZZ') 
    '''
    dcb_fname = outFilename.split('.bin')[0] + '.DCB'
    outRows = [[], [str(nBytesPerRow)]]

    col_names = df.columns.to_list() # to keep the correct order

    #---replacing the relevant 'int' cols with datetime cols
    if len(dt_cols) > 0:
        for col_name in dt_cols:
            col_dtypes[col_name] = 'datetime64'
            del col_dtypes[col_name + '__date__'], col_dtypes[col_name + '__time__']
            # removing the _'date' and '_time' column names
            idx = col_names.index(col_name + '__date__')
            col_names[idx] = col_name
            del col_names[idx + 1] # '_time'

    # --map from np to TC
    write_type_map = {'int': 'I', 'float': 'F', 'S': 'C', 'datetime': 'DateTime'}

    # each row contains (refer TC manual for details)
    # name, type, start, width, decimals, disp width, disp decimals
    # format, agg method, descr, defaul val, j/s method, disp name ===> all empty for now TODO: fix?
    byte_count = 1
    for col_name in col_names:
        col_type = col_dtypes[col_name]
        col_bytes = int(''.join([ch for ch in col_type if ch.isdigit()]))  # num of bits/bytes
        temp_types = [v for k, v in write_type_map.items() if k in col_type]
        assert len(temp_types) == 1, " More than one or no possibility for col_name: {0} and type {1}".format(col_name, col_type)
        out_type = temp_types[0]

        # ---the digits are bytes for C col and bits for others
        col_bytes = col_bytes//8 if out_type != 'C' else col_bytes

        #--handling real type
        out_type = 'R' if (col_bytes == 8 and out_type == 'F') else out_type

        # ---disp width and disp decimals
        disp_wd = col_bytes + 4 if out_type != 'DateTime' else col_bytes + 12
        disp_dec = 4 if (out_type == 'F' or out_type == 'R') else 0

        outRow = ['"' + str(col_name) + '"', out_type, byte_count, col_bytes, 0, disp_wd, disp_dec] + ['', '""', '""', '', '""', '']
        outRows.append(outRow)

        #print("+++ Testing the dcb rows: ", col_name, out_type, byte_count, col_bytes)
        byte_count += col_bytes

    assert byte_count - 1 == nBytesPerRow, "The byte count of columns does not add up {0} != {1}".format(byte_count - 1, nBytesPerRow)
    # ---writing to the file
    with open(dcb_fname, 'w') as ofile:
        for row in outRows:
            row_str = [str(item) for item in row]
            row_str = ','.join(row_str)
            print(row_str, file=ofile)


# ======================================================================================================

def set_na_str_values(df):
    '''
        sets NA values to the MISS constant above for float and int cols
        converts the string columns to binary strings for writing
    '''

    contains_na = (df.isna().sum().sum() > 0)

    col_list = list(df.columns)
    col_types = [str(i).lower() for i in df.dtypes.values]

    SHORT_MISS = -32767
    LONG_MISS = -2147483647
    FLT_MISS = -3.4028234663852886e+38
    DBL_MISS = -1.7976931348623158e+308
    CODING  = 'windows-1252'
    
    for i in range(len(col_list)):
        col_name = col_list[i]
        col_type = col_types[i]
        # --handling NAs in integer
        if ('int' in col_type) and contains_na:
            n_bits = col_type.split('int')[1]
            if n_bits == '16':
                miss_val = SHORT_MISS
            elif n_bits == '32':
                miss_val = LONG_MISS
            else:
                raise TypeError("Gisdk binary tables only support integers of 1, 2 or 4 bytes ! The bytes of col {0} are {1}". format(col_name, n_bits))

            df.loc[df[col_name].isna(), col_name] = miss_val

        # ---handling NAs in float columns
        if ('float' in col_type) and contains_na:
            n_bits = col_type.split('float')[1]
            if n_bits == '32':
                miss_val = FLT_MISS
            elif n_bits == '64':
                miss_val = DBL_MISS

            df.loc[df[col_name].isna(), col_name] = miss_val

        # ---handling string columns
        # None to ''
        # strings -> binary strings
        if 'object' in col_type:
            if contains_na:
                df.loc[df[col_name].isna(), col_name] = ''
            df[col_name] = df[col_name].str.encode(CODING)

    # ---returning df with na's set to MISS_VALS
    return df

#========================================================================================================

def set_dt_values(df):
    '''
        converts the datetime cols to two sepeate date and time columns each represented as 32 bit integers
    '''

    dt_cols = list(df.dtypes[df.dtypes == "datetime64[ns]"].index)

    #---Converting the datetime to integers for TC
    for col_name in dt_cols:
        df[col_name + '__date__'] = ((df[col_name].dt.date).astype('str')).str.replace('-','')
        df[col_name + '__date__'].mask(df[col_name + '__date__'] == 'NaT', None, inplace = True)
        df[col_name + '__date__'] = df[col_name + '__date__'].astype('float').astype('Int32') #TODO: fix float convertion in future pd versions

        df[col_name + '__time__'] = ( (df[col_name] - df[col_name].dt.floor('D')).dt.total_seconds() * 1000 ).astype('float32').astype('Int32')

        df.drop(columns = col_name, inplace = True)
    
    return df

#========================================================================================================
