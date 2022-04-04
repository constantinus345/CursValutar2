from USERS_DFs_forms import APL_and_Codes
from difflib import get_close_matches

APL_List_all = [x.split(",")[0] for x in APL_and_Codes()["APLs"]]
APL_Code_all = APL_and_Codes()["Codes"]

print(len(APL_List_all))
print(len(APL_Code_all))

def aplname_from_code(code):
    cod_index= APL_Code_all.index(code)
    APL_name = APL_List_all[cod_index]
    return APL_name




def guessing_apl(name):
    Close_Match= get_close_matches(name, APL_List_all, n=2, cutoff=0.1)[0]
    return [Close_Match, APL_Code_all[APL_List_all.index(Close_Match)]]