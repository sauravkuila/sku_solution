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
    print(df.loc[:,'Qty'])
    for idx in df.index:
        size = df.loc[idx,'Size']
        pc = df.loc[idx,'PackConfig']
        pack_dict[size] = pc
    print(pack_dict)
    return df['PackConfig']

if __name__ == "__main__":
    print('Starting SKU setup')
    

    src = input('path of data file: ')
    src = src.replace('"','')
    #check if file exists and can be read
    if False == os.path.exists(src):
        raise(Exception('file not found'))
    fileobj = pd.read_excel(src)

    #create a dataframe for the columns in observation
    df = fileobj.loc[:,["Store","Style Color","Qty","Size"]]    
    df['Product'] = df['Style Color'].astype(str)+'_'+df['Qty'].astype(str)

    #for the test, seclude dataframe to store1
    store1 = df[df['Store'] == 'Store 1']
    totalQty = store1['Qty'].sum()
    uniqueItems = len(store1)
    print('unique item demand from store1: ', uniqueItems)

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
    unique_stores = df['Store'].unique()
    for store in unique_stores:
        if pd.isna(store):
            print('as')
    unique_styles = df['Style Color'].unique()
    print(unique_stores)
    print(unique_styles)
    style1 = store1[store1['Style Color'] == 'Mens Blue Sparrow Print Grey']
    print(style1)
    generate_pack_ratio(style1, container_size)
    
    
    #computing number of containers required
    # cntr_float = totalQty%container_size
    # if cntr_float >= 0.7 * container_size:
    #     containers = math.ceil(totalQty/container_size)
    # else:
    #     containers = math.floor(totalQty/container_size)
    # print('TotalProducts: {0} \t ContainerSize(y): {1} \t TotalContainers: {2}'.format(totalQty, container_size, containers))

    # #very important step, here the assumption is objects are prioritized based on qty from a store
    # #the sorting can be done based on relevant priority (cost, size, any other combination)
    # store1 = store1.sort_values(by=['Qty'],ascending=False)
    # generate_product_container_qty(store1, containers, container_size)
    # print(store1)

    # minima = store1['LossOfSales'].sum() + store1['ExcessInventory'].sum()
    # print(minima)

    # # minima = calculate_minima(store1, containers)
    # # print(store1)
    # store1.to_excel('store1.xlsx')

