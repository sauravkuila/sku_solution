import pandas as pd
import numpy as np
from tqdm import tqdm
import os, math, time
import progressbar

import warnings
warnings.filterwarnings("ignore")

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
    # return df['PackConfig']
    return pack_dict

def calculate_minima(df, pack_ratio):
    df['PackConfig'] = 0
    df['ItemsPacked'] = 0
    df['LossOfSales'] = df['Qty']
    df['ExcessInventory'] = 0
    df['LosEi'] = df['ExcessInventory']+df['LossOfSales']
    # df[df['Size'] == 'XS','PackConfig'] = pack_ratio['XS']
    # df[df['Size'] == 'S','PackConfig'] = pack_ratio['S']
    # df[df['Size'] == 'M','PackConfig'] = pack_ratio['M']
    # df[df['Size'] == 'L','PackConfig'] = pack_ratio['L']
    # df[df['Size'] == 'XL','PackConfig'] = pack_ratio['XL']
    # df[df['Size'] == 'XXL','PackConfig'] = pack_ratio['XXL']

    for idx in df.index:
        size = df.loc[idx,'Size']
        df.loc[idx,'PackConfig'] = pack_ratio[size]
        df.loc[idx,'ItemsPacked'] = df.loc[idx,'PackConfig'] * df.loc[idx,'TotalPacks']
        df.loc[idx,'LossOfSales'] = max(0, df.loc[idx,'Qty'] - df.loc[idx,'ItemsPacked'])
        df.loc[idx,'ExcessInventory'] = max(0, df.loc[idx,'ItemsPacked'] - df.loc[idx,'Qty'])
        df.loc[idx,'LosEi'] = df.loc[idx,'LossOfSales'] + df.loc[idx,'ExcessInventory']
    # print(df)
    return df['LosEi'].sum()


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
        pack_size = int(cs)
        if pack_size < 0:
            raise(Exception('negative pack size cannot be computed'))
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
            # print(unique_stores)
            ratio_combi = {}
            for store in unique_stores:
                if pd.isna(store) == False:
                    print('running for store :{0}'.format(store))
                    store_df = dc_df[dc_df['Store'] == store]
                    unique_styles = store_df['Style Color'].unique()
                    # print(unique_styles)
                    for style in unique_styles:
                        if pd.isna(store) == False:
                            print('running for style :{0}'.format(style))
                            style_df = store_df[store_df['Style Color'] == style]
                            #find the pack ration for style
                            pack_ratio = generate_pack_ratio(style_df, pack_size)

                            #calculate the packs required for the style
                            style_sum = style_df['Qty'].sum()
                            style_packs = math.floor(style_sum/pack_size)
                            #update the packs in df
                            style_df.loc[:,'TotalPacks'] = style_packs

                            #update the new style df to dc df for managing packs for the style for each style-store combination
                            dc_df[(dc_df['Store'] == store) & (dc_df['Style Color'] == style)] = style_df

                            #save the pack ratio to simulate later
                            ratio_combi[store+'_'+style] = pack_ratio
            # print(ratio_combi)
            # print(dc_df)
            lowest_minima = dc_df['Qty'].sum()
            best_pack_ratio = ''
            #iterate these ratios to calculate the lowest minima in the entire dataset
            for ratio in ratio_combi:
                print('calculating minima for {0} with ratio {1}'.format(dc,pack_ratio))
                pack_ratio = ratio_combi[ratio]
                minima = calculate_minima(dc_df,pack_ratio)
                if minima < lowest_minima:
                    lowest_minima = minima
                    best_pack_ratio = ratio

            print('lowest minima({0}) best pack ratio is {1} as {2}'.format(lowest_minima,best_pack_ratio,ratio_combi[best_pack_ratio]))

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
    
    

