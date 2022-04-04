import urllib
from os import listdir

urls_docs_str= "1972739, 1972572, 1972565"

def list_from_urls_docs_str(urls_docs_str):
    urls_docs_lis = [ x.replace(" ","") for x in str(urls_docs_str).split(",")]
    return urls_docs_lis

def download_pdf_rsal_list(urls_docs_str, Folder= "E:/RSAL/Dispozitii_PDF"):
    
    PDFs_Paths = []
    
    try:
        urls_docs_lis = list_from_urls_docs_str(urls_docs_str)
        for pdf in urls_docs_lis:
            Disp_PDF= f"https://actelocale.gov.md/ral/act/downloadAct/{pdf}"
            File_PDF=f'{Folder}/{pdf}.pdf'
            if f"{pdf}.pdf" not in listdir("E:/RSAL/Dispozitii_PDF"):
                urllib.request.urlretrieve( Disp_PDF, File_PDF)
                print(f"downloaded {pdf}")
            else:
                print(f"already there {pdf}")
            
            PDFs_Paths.append(File_PDF)
    except Exception as e:
        print(e)
    
    return PDFs_Paths

import sys
if __name__ == "__main__":
    print("Executing the main")
else: 
    print(f"Imported {sys.argv[0]}")