import pandas as pd
from tqdm import tqdm
import os, math, time
import progressbar

def generate_product_container_qty(df, total_containers, single_container_size):
    df['ProductPerContainer'] = 0
    df['TotalProductShipped'] = df['ProductPerContainer'] * total_containers
    df['LossOfSales'] = df['Qty']
    df['ExcessInventory'] = 0
    
    remaining_size = single_container_size

    widgets = ['Populating containers per product (x): ', progressbar.AnimatedMarker()]
    bar = progressbar.ProgressBar(widgets=widgets,maxval=single_container_size*total_containers).start()
    
    for i, row in enumerate(df.loc[:,'Qty']):
        qty = df.loc[i,'Qty']
        prod_added = math.floor(qty/total_containers)
        if prod_added == 0:
            prod_added = 1

        # df.loc[i,'product_per_container'] += prod_added
        df.loc[i,'ProductPerContainer'] += prod_added

        # total_product_shipped = df.loc[i,'product_per_container'] * total_containers
        total_product_shipped = df.loc[i,'ProductPerContainer'] * total_containers
        loss_of_sale = max(0, df.loc[i,'Qty'] - total_product_shipped)
        excss_inventory = max(0, total_product_shipped - df.loc[i,'Qty'])

        #update the max(0, Q-xy) and max(0, xy-Q) condition
        df.loc[i,'TotalProductShipped'] = total_product_shipped
        df.loc[i,'LossOfSales'] = loss_of_sale
        df.loc[i,'ExcessInventory'] = excss_inventory

        remaining_size = remaining_size - prod_added
        bar.update(single_container_size - remaining_size)
        # print(df)
        if remaining_size <= 0:
            break

    while (remaining_size > 0):
        max_idx = df['LossOfSales'].idxmax()
        df.loc[max_idx,'ProductPerContainer'] += 1
        df.loc[max_idx,'TotalProductShipped'] = df.loc[max_idx,'ProductPerContainer'] * total_containers
        df.loc[max_idx,'LossOfSales'] = max(0, df.loc[max_idx,'Qty'] - df.loc[max_idx,'TotalProductShipped'])
        df.loc[max_idx,'ExcessInventory'] = max(0, df.loc[max_idx,'TotalProductShipped'] - df.loc[max_idx,'Qty'])
        # print(df)
        remaining_size = remaining_size - 1
        bar.update(single_container_size - remaining_size)

if __name__ == "__main__":
    print('Starting SKU setup')
    

    src = input('path of data file: ')
    src = src.replace('"','')
    #check if file exists and can be read
    if False == os.path.exists(src):
        raise(Exception('file not found'))
    fileobj = pd.read_excel(src)

    #create a dataframe for the columns in observation
    df = fileobj.loc[:,["Store","Style Color Size","Qty"]]    
    df['Product'] = df['Style Color Size'].astype(str)+'_'+df['Qty'].astype(str)

    #for the test, seclude dataframe to store1
    store1 = df[df['Store'] == 'Store 1']
    totalQty = store1['Qty'].sum()
    uniqueItems = len(store1)
    print('unique item demand from store1: ', uniqueItems)

    cs = input('enter the products going in a container (y): ')
    #check if size entered was an integer
    try:
        container_size = int(cs)
        if container_size < 0:
            raise(Exception('negative containers cannot be computed'))    
    except Exception as e:
        print('case size not integer', e)
        raise(e)

    
    
    #computing number of containers required
    cntr_float = totalQty%container_size
    if cntr_float >= 0.7 * container_size:
        containers = math.ceil(totalQty/container_size)
    else:
        containers = math.floor(totalQty/container_size)
    print('TotalProducts: {0} \t ContainerSize(y): {1} \t TotalContainers: {2}'.format(totalQty, container_size, containers))

    #very important step, here the assumption is objects are prioritized based on qty from a store
    #the sorting can be done based on relevant priority (cost, size, any other combination)
    store1 = store1.sort_values(by=['Qty'],ascending=False)
    generate_product_container_qty(store1, containers, container_size)
    print(store1)

    minima = store1['LossOfSales'].sum() + store1['ExcessInventory'].sum()
    print(minima)

    # minima = calculate_minima(store1, containers)
    # print(store1)
    store1.to_excel('store1.xlsx')

