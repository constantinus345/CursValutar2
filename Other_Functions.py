def Diff_Lists(li1, li2):
    li_dif = [i for i in li1 + li2 if (i in li1 and i not in li2)]
    return li_dif
 

import sys
if __name__ == "__main__":
    print("Executing the main")
else: 
    print(f"Imported {sys.argv[0]}")