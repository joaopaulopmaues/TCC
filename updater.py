from downloader import search_n_download_file

def download_submit_delete(hashin,browser):
    search_n_download_file(hashin,browser)#downloads ransomware and updates hasheslist.csv

#check the third column. if the value of the second column is in the third, submit for cuckoo and substitute the value of the third column by the value returned by send_file (url to know the status)