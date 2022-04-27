print(3+4)



def best_first_offer_dict(tip, vorc, valuta, topx=1):
    """
    tip= banci or csv ; 
    vorc= cump or vanz; 
    valuta ABC
    returs Dataframe with topx biggest values 
    """


    dfx_topx = best_offer(tip, vorc, valuta, topx)
    
    offer_dic = best_offer(tip, vorc, valuta, topx).to_dict(orient="list")
    #tip replace?
    return offer_dic

def generate_text_best_offer(tip, vorc, valuta, topx=1):

    best_dic= best_first_offer_dict(tip, vorc, valuta, topx=1)
    #print(best_dic)


    try:
        if vorc[0] == "cump":
            str_institutie_tip_oferta = tip[0].replace("banci","Banca").replace("csv","Casa de schimb")
            str_oferta_float = int(best_dic['cump'][0])/10000
            str_oferta = f"""{str_institutie_tip_oferta} cumpără {valuta[0].upper()} cu {str_oferta_float}
            \n(Dvs. vindeți {valuta[0].upper()})""".replace("  ","")
        elif vorc[0] == "vanz":
            str_institutie_tip_oferta = tip[0].replace("banci","Banca").replace("csv","Casa de Schimb")
            str_oferta_float = int(best_dic['vanz'][0])/10000
            str_oferta = f"""{str_institutie_tip_oferta} vinde {valuta[0].upper()} cu {str_oferta_float}
            \n(Dvs. cumpărați {valuta[0].upper()})""".replace("  ","")
        else:
            str_oferta= ""
    except Exception as err1:
        str_oferta= ""
        print(f"!!! Error = {err1}")

    str_institutie_tip = tip[0].replace("banci","bancă").replace("csv","casă de schimb valutar")
    str_operatiune = vorc[0].replace("vanz", "vânzare").replace("cump", "cumpărare")
    #Maybe change str_operatiune to opposite, given bank selling= customer buying? Confusing
    str_valuta = valuta[0].upper()
    try:
        str_date = best_dic["data_curs"][0].strftime('%d-%b-%Y')
    except:
        str_date = datetime.datetime.now().strftime('%d-%b-%Y')

    nr_institutii= len(best_dic["cump"])

    if nr_institutii == 1:
        reply_best = f"""Cel mai bun curs valutar pentru Dumneavostră:
        tipul instituției : {str_institutie_tip}
        data : {str_date}
        valuta : {str_valuta}
        este la {best_dic["denumire"][0]} ({str_institutie_tip})
        {str_oferta}
            """.replace("  ","")


    elif nr_institutii >1:
        str_denumiri= f"({nr_institutii} instituții):"
        for index_denumire, val in enumerate(best_dic["denumire"]):
            str_denumiri += f"\n{val}"
        
        reply_best = f"""Cel mai bun curs valutar pentru Dumneavostră::
        tipul instituției : {str_institutie_tip}
        data : {str_date}
        valuta : {str_valuta}
        {str_denumiri}
        {str_oferta}
            """.replace("  ","")

    else: 
        reply_best= ""
    return reply_best

print(best_offer(["banci"], ["vanz"],"USD",topx=1))
print(generate_text_best_offer(["banci"], ["cump"], ["EUR"], 10))
