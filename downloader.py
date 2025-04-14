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
        if row and row[0] == s:  # Check if row exists and first column matches
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

def search_n_download_file(hashin,browser): #including Cuckoo's JSON report
    integrations=["pikker","vs","tria.ge","ha"]
    for api in integrations:
        match api:
            case "pikker": #Cuckoo Sandbox
                task_id = cuckoo_db.search(hashin,browser)
                if task_id != "Not_Found":
                    sample=task_id+'.zip/reports/report.json'
                    update_csv(hashin,sample) # write the filename and path to the report in Hasheslist.csv
                    return "Report_submitted!"
            case "vs": #VirusShare
                sample=vs.download_sample(hashin,browser)
                if ".zip" in sample:
                    update_csv(hashin,sample) # write the filename in Hasheslist.csv
                    return "Ready_for_submission!"
            case "tria.ge": #Tria.ge
                sample=tg.download_sample(hashin)
                if ".zip" in sample:
                    update_csv(hashin,sample)
                    return "Ready_for_submission!"
            case "ha": #Hybrid-Analysis
                sample=ha.download_sample(hashin,browser)
                if ".sample" in sample:
                    update_csv(hashin,sample)
                    return "Ready_for_submission!"