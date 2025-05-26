from triage import Client
import os

url = "https://api.tria.ge"
token = os.getenv("TRIAGETOKEN") #"9d13b781fa843f8811e8a4c0776750b1e351937b"
download_dir = os.getenv("DOWNLOAD_DIR")
malware_folder = os.getenv("MALWARE_DST")
c = Client(token, root_url=url)


#hashin="88ee23d0001b325653602351eb898af0ab82a7f8c2413d1f44fea7557c46eabb"

def download_sample(hashin):
    aux = c.search('sha256:'+hashin)
    try:
        dict_aux = next(aux)
        sample_id = dict_aux['id']
        t = c.get_sample_file(sample_id) #it doesn't need download_monitor because the file isn't downloaded.
        if not os.path.exists(download_dir+malware_folder):
            # Create the folder
            os.makedirs(download_dir+malware_folder)
        with open(download_dir+malware_folder+hashin+"_pw_infected.zip", "wb") as f: #its bytes are streamed and stored in a variable
            f.write(t)
        return download_dir+malware_folder+hashin+"_pw_infected.zip"
    except:
        return "Not_Found"