import csv
from datetime import datetime, timedelta
from valhalla_integration import valhalla
import pandas as pd
import os
import time

#import the integration you developed

def hash_searcher(browser,familyname,date='0000-00-00',quant=5):
    hashes_set=set([])
    integrations=['valhalla'] #add integrations' name. And don't forget to include a case in which the integration doesn't find any hash sample
    for api in integrations:
        match api: #add cases with your integrations' name and the function to retrieve the hash list
            case 'valhalla':    
                aux=valhalla(browser,familyname,date,quant)
        hashes_set.update(aux)
    return hashes_set

def hash_enumerator(browser, familylist, date='0000-00-00', quant=5, force=False,csv_file='hasheslist.csv',t=60):
    
    # Check and update CSV file
    today = datetime.now().strftime('%Y-%m-%d')
    
    try: # Read the first line to check last update date
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            first_line = next(reader, None)
            
            if first_line and not force:
                last_date_str = first_line[0]
                try:
                    last_date = datetime.strptime(last_date_str, '%Y-%m-%d')
                    if (datetime.now() - last_date) < timedelta(weeks=3):
                        return ''  # Recent update exists and no specific date requested
                except ValueError:
                    pass  # Invalid date format, proceed with update
    except FileNotFoundError:
        with open(csv_file,'a+') as nf:
            nf.write(today)
        pass  # File doesn't exist, we'll create it
    # Check if file exists and if it ends with a newline
    needs_newline = False
    with open(csv_file, 'rb') as file:
        file.seek(-1, os.SEEK_END)  # Check last byte
        if file.read(1) != b'\n':
            needs_newline = True
    with open(csv_file, 'a', newline='') as file:
        file.write('\n')
    df = pd.read_csv(csv_file,header=None,skiprows=1)
    hashes = set(df.iloc[:,1])
    # Process each family
    for family in familylist:
        h = hash_searcher(browser, family, date, quant)
        if not h:  # Empty result
            # Write "Not_Found,family" to CSV
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([family,"Not_Found"])
        else:
            # Add hashes to the set and write "hash,family" to CSV
            h = h - hashes
            with open(csv_file, 'a', newline='') as f:
                writer = csv.writer(f)
                for hash_value in h:
                    writer.writerow([family,hash_value])
            hashes.update(h)
        time.sleep(t)
    
    # Update the first line with today's date
    # We need to read all lines first, then rewrite with new date
    with open(csv_file, 'r') as f:
        lines = f.readlines()
    with open(csv_file, 'w') as f:
        # Write all lines back with date update
        f.writelines([today+'\n']+lines[1:])
    
    return 'File updated!'