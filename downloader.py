import csv
import sandboxpikker as cuckoo_db
import hybrid_analysis as ha
import triage_integration as tg
import virusshare as vs

def update_csv(s, v, filename='hasheslist.csv'):
    updated = False
    rows = []
    
    # Read the file
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        rows = list(reader)  # Load all rows
    
    # Search and update
    for row in rows:
        if len(row)<2:
            continue
        elif row and row[1] == s:  # Check if row exists and first column matches
            while len(row) < 3:  # Ensure row has at least 3 columns
                row.append('')
            row[2] = v  # Update third column (0-based index 2)
            updated = True
            break  # Stop after first match
    
    # Write back only if updated
    if updated:
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)

#go install github.com/hatching/triage/go/cmd/triage@latest
#triage authenticate $TOKEN
#triage file $hash download file -o 'path/to/file.zip' it is always a zip with infected as password

def search_n_download_file(hashin,browser,logged=False): #including Cuckoo's JSON report
    #integrations=["pikker","vs","tria.ge","ha"]
    integrations=["pikker","tria.ge","ha"]
    for api in integrations:
        match api:
            case "pikker": #Cuckoo Sandbox
                sample = cuckoo_db.search(hashin,browser)
                if sample != "Not_Found":
                    update_csv(hashin,sample) # write the filename and path to the report in Hasheslist.csv
                    return sample
            case "vs": #VirusShare
                sample=vs.download_sample(hashin,browser,logged=logged)
                if ".zip" in sample:
                    update_csv(hashin,sample) # write the filename in Hasheslist.csv
                    return sample
            case "tria.ge": #Tria.ge
                sample=tg.download_sample(hashin)
                if ".zip" in sample:
                    update_csv(hashin,sample)
                    return sample
            case "ha": #Hybrid-Analysis
                sample=ha.download_sample(hashin,browser,logged=logged)
                if ".sample" in sample:
                    update_csv(hashin,sample)
                    return sample
    update_csv(hashin,"Not_Found")
    return "Not_Found"