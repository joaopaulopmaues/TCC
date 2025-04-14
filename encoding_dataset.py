import pandas as pd
from sklearn.preprocessing import LabelEncoder


def unite_csvs_into_csv(list_of_paths,output_path="/Users/joaopaulopmaues/Downloads/tensorflow-test/TCC/XRan/XRan-main/wholeDataset.csv"):
    # Inicializa uma lista para armazenar os DataFrames
    dataframes = []
    L = list_of_paths

    # Itera pela lista de arquivos CSV
    for arquivo in L:
        # Lê o arquivo CSV ignorando a primeira linha (cabeçalho)
        df = pd.read_csv(arquivo, skiprows=1, header=None)
        dataframes.append(df)

    # Une os DataFrames da lista, preservando a ordem
    df_final = pd.concat(dataframes, ignore_index=True)

    # Adiciona o cabeçalho de L[0] no DataFrame resultante
    header = pd.read_csv(L[0], nrows=0).columns
    df_final.columns = header

    # Escreve o DataFrame final em um novo arquivo CSV
    df_final.to_csv(output_path, index=False)
    
def faux(x):
    for el in x:
        x[x.index(el)]=str(el)
    return x    

def encode_csv_to_binary_df(path_whole_dataset): # a DataFrame with the headers not encoded but the values are binaries
    df = pd.read_csv(path_whole_dataset, sep=';',low_memory=False)
    df_copy = df.copy()
    tuple_list=[(0,500),(500,510),(510,520)]
    encLen=0
    for e in tuple_list:
        n1=e[0]
        n2=e[1]
        aux=[]
        for i in range(n1,n2):
            aux+=df.iloc[:,i].unique().tolist()
        dfaux=pd.DataFrame(aux)
        dfaux=pd.DataFrame(dfaux.iloc[:,0].unique().tolist())
        label_encoder=LabelEncoder()
        dfaux[1]=label_encoder.fit_transform(dfaux.loc[:,0])
        dfaux[1] = dfaux[1].apply(lambda x: format(x, 'b'))
        dfaux[1] = dfaux[1].apply(lambda x: [int(i) for i in x])
        laux=dfaux[1].str.len().max()
        if encLen<laux:
            encLen=laux
    laux=encLen
    for e in tuple_list:
        n1=e[0]
        n2=e[1]
        aux=[]
        for i in range(n1,n2):
            aux+=df.iloc[:,i].unique().tolist()
        dfaux=pd.DataFrame(aux)
        dfaux=pd.DataFrame(dfaux.iloc[:,0].unique().tolist())
        label_encoder=LabelEncoder()
        dfaux[1]=label_encoder.fit_transform(dfaux.loc[:,0])
        dfaux[1] = dfaux[1].apply(lambda x: format(x, 'b'))
        dfaux[1] = dfaux[1].apply(lambda x: [int(i) for i in x])
        dfEncode=dfaux.set_index(0).T
        dfDecode=pd.DataFrame({0:['NaN']*len(dfaux[0]),1:dfaux[0]})
        def faux(x):
            for el in x:
                x[x.index(el)]=str(el)
            return x
        dfaux[1]=dfaux[1].apply(lambda x: faux(x))
        dfDecode[0]=dfaux[1].apply(lambda x:''.join(x))
        dfDecode[0]=dfDecode[0].str.zfill(laux)
        dfDecode=dfDecode.set_index(0).T
        def pad_list(lst,leng):
            return [0] * (leng - len(lst)) + lst if len(lst) < leng else lst
        dfEncode.loc[1]=dfEncode.loc[1].apply(lambda x: pad_list(x,laux))
        # Criar o mapeamento entre as palavras e as listas binárias
        word_to_binary = {col: dfEncode[col].iloc[0] for col in dfEncode.columns}

        # Substituir palavras por listas de binários nas 500 primeiras colunas
        df_copy.iloc[:, n1:n2] = df_copy.iloc[:, n1:n2].applymap(lambda x: word_to_binary.get(x, x))
    return df_copy

def encoding_processed_json(output_paths,input_path): # after all the jsons are processed and turned into one big csv,
                                        # the csv is received and turned into binary encoded matrices in the form of csvs
    df_copy=encode_csv_to_binary_df(input_path)
    dfx=df_copy.copy()
    cols_to_expand=dfx.iloc[:,:520]
    # Dividing each column in multiple columns
    expanded_columns = pd.DataFrame(cols_to_expand.stack().tolist(), index=cols_to_expand.stack().index).reset_index(drop=True)
    
    def gen_csvs_14_for_one_dataset(filename,dfx,nsample=1):
        def process_sample_sequential_v2(df, bits_per_word, padding_value, separator_row, npaddingrows=18):
            def transform_section(n_lines, start_row):
                """Returns a section in the expected format."""
                section = df.iloc[start_row:start_row + n_lines].values.tolist()
                return section

            # Defining the sections and fullfilling
            result = []
            row_cursor = 0  # Tracking the position in original DataFrame
            
            # |A|: 500 lines
            result.extend(transform_section(500, row_cursor))
            row_cursor += 500
            i=0
            while i<npaddingrows:
                result.append(separator_row)  # Padding row
                i+=1

            # |D|: 10 lines
            result.extend(transform_section(10, row_cursor))
            row_cursor += 10
            i=0
            while i<npaddingrows:
                result.append(separator_row)  # Padding row
                i+=1

            # |M|: 10 lines
            result.extend(transform_section(10, row_cursor))
            row_cursor += 10

            # Making sure the resulting file has the appropriate quantity of lines
            #assert len(result) == 522, f"Error at the final size of the sample: {len(result)} lines generated."
            assert len(result) == 520+(2*npaddingrows), f"Error at the final size of the sample: {len(result)} lines generated."
            return pd.DataFrame(result)

        # Processing all samples
        rows_per_sample = 520  # Each sample has 520 lines
        new_cols = 14  # Quantity of columns in the final format
        bits_per_word = 14
        padding_value = -1
        separator_row = [padding_value] * new_cols  # A line for padding

        #output_folder = "VirusShare_14x522"
        #os.makedirs(output_folder, exist_ok=True)

        #nsample = 0  # Sample counter
        for sample_idx in range(0, len(dfx), rows_per_sample):
            sample = dfx.iloc[sample_idx:sample_idx + rows_per_sample]  # Extract the current sample
            
            # Processing the sample into the format 14x522
            processed_sample = process_sample_sequential_v2(sample, bits_per_word, padding_value, separator_row)
        
            # Saving the result as CSV
            filenames = f"{filename}/Sample_{nsample}.csv"
            processed_sample.to_csv(filenames, index=False, header=False)
            nsample += 1
    #        print(f"Saved sample: {filenames}")
            
    filenames=output_paths
    if type(output_paths)==list: #this means that the dataset is the one from XRan article
        idx=[(0,520*6263),(520*6263,520*(6263+668)),(520*(6263+668),520*(6263+668+8443)),(520*(6263+668+8443),520*(6263+668+8443+14797))]
        i=0
        while(i<len(output_paths)):
            begin=idx[i][0]
            end=idx[i][1]
            dfx_aux=expanded_columns.iloc[begin:end].copy()
            saux=filenames[i]
            gen_csvs_14_for_one_dataset(saux,dfx_aux)
            i+=1
    elif type(output_paths)==str: #this means that the dataset is the one collected by the updater API
        gen_csvs_14_for_one_dataset(filenames,expanded_columns)
    else:
        print("Unexpected input type!")