import pandas as pd
import numpy as np
from tqdm import tqdm
import os, math, time
import progressbar

# ItemsPacked- x*y
# PackConfig - x
# TotalPacks - y
# PackSize

def generate_pack_ratio(df, pack_size):
    df['PackConfig'] = 0
    df['ItemsPacked'] = 0
    df['LossOfSales'] = df['Qty']
    df['ExcessInventory'] = 0
    df['LosEi'] = df['ExcessInventory']+df['LossOfSales']

    total_qty = df['Qty'].sum()
    total_packs = math.floor(total_qty/pack_size)
    
    pack_size_remaining = pack_size

    while (pack_size_remaining > 0):
        max_idx = df['LossOfSales'].idxmax()
        df.loc[max_idx,'PackConfig'] += 1
        df.loc[max_idx,'ItemsPacked'] = df.loc[max_idx,'PackConfig'] * total_packs
        df.loc[max_idx,'LossOfSales'] = max(0, df.loc[max_idx,'Qty'] - df.loc[max_idx,'ItemsPacked'])
        df.loc[max_idx,'ExcessInventory'] = max(0, df.loc[max_idx,'ItemsPacked'] - df.loc[max_idx,'Qty'])
        pack_size_remaining = pack_size_remaining - 1
    
    # print(df.loc[:,['Size','PackConfig']])
    pack_dict = {}
    # print(df.loc[:,'Qty'])
    for idx in df.index:
        size = df.loc[idx,'Size']
        pc = df.loc[idx,'PackConfig']
        pack_dict[size] = pc
    print(pack_dict)
    return df['PackConfig']

def calculate_minima(df, pack_ratio):
    df[df['Size'] == 'XS','Size'] = pack_ratio['XS']
    df[df['Size'] == 'S','Size'] = pack_ratio['S']
    df[df['Size'] == 'M','Size'] = pack_ratio['M']
    df[df['Size'] == 'L','Size'] = pack_ratio['L']
    df[df['Size'] == 'XL','Size'] = pack_ratio['XL']
    df[df['Size'] == 'XXL','Size'] = pack_ratio['XXL']

if __name__ == "__main__":
    print('Starting SKU setup')
    

    src = input('path of data file: ')
    src = src.replace('"','')
    #check if file exists and can be read
    if False == os.path.exists(src):
        raise(Exception('file not found'))
    fileobj = pd.read_excel(src)

    #create a dataframe for the columns in observation
    df = fileobj.loc[:,["Store","DC","Style Color","Qty","Size"]]

    #for the test, seclude dataframe to store1
    store1 = df[df['Store'] == 'Store 1']
    # totalQty = store1['Qty'].sum()
    # uniqueItems = len(store1)
    # print('unique item demand from store1: ', uniqueItems)

    cs = input('enter the pack size: ')
    #check if size entered was an integer
    try:
        container_size = int(cs)
        if container_size < 0:
            raise(Exception('negative containers cannot be computed'))
    except Exception as e:
        print('case size not integer', e)
        raise(e)

    # print(store1)
    unique_dc = df['DC'].unique()
    for dc in unique_dc:
        if pd.isna(dc) == False:
            print('running for dc :{0}'.format(dc))
            dc_df = df[df['DC'] == dc]
            dc_df['TotalPacks'] = 0
            unique_stores = dc_df['Store'].unique()
            print(unique_stores)
            for store in unique_stores:
                if pd.isna(store) == False:
                    print('running for store :{0}'.format(store))
                    store_df = dc_df[dc_df['Store'] == store]
                    unique_styles = store_df['Style Color'].unique()
                    print(unique_styles)
                    for style in unique_styles:
                        if pd.isna(store) == False:
                            print('running for style :{0}'.format(style))
                            style_df = store_df[store_df['Style Color'] == style]
                            print(style_df)
                            pack_ratio = generate_pack_ratio(style_df, container_size)

                            # style_sum = style_df['Qty'].sum()
                            # print(style_sum)
                            # #ask me later how this works (will take time to explain. in short, filtered dataframe of a filtered dataframe)
                            # print((dc_df[dc_df['Store'] == store])[(dc_df[dc_df['Store'] == store])['Style Color'] == style])
                            # ((dc_df[dc_df['Store'] == store])[(dc_df[dc_df['Store'] == store])['Style Color'] == style])['TotalPacks'] = style_sum
                            # print(dc_df[dc_df['Store'] == store][(dc_df[dc_df['Store'] == store])['Style Color'] == style])
                            # # dc_df[dc_df[dc_df['Store'] == store]['Style Color'] == style, 'TotalPacks'] = style_df['Qty'].sum()
                            # print(dc_df)
                            # #apply this ratio to entire stores in dc and calculate minima
                            # #calculate individually total packs needed per style
                             
                    
    style1 = store1[store1['Style Color'] == 'Mens Blue Sparrow Print Grey']
    print(style1)
    generate_pack_ratio(style1, container_size)
    
    

