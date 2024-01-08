from datetime import datetime
import requests
from os import path,remove,system,makedirs

if not path.exists("Downloads"):
      makedirs("Downloads")

FROM = "MST Automations"
NOTES = "Thankyou For Shopping with us. Our agent Will call you soon."
TERMS = "MST Automations Holds Right to Cancel/Delay your order anytime."
URL = "https://invoice-generator.com"
LOGO = "https://as1.ftcdn.net/v2/jpg/04/42/89/20/1000_F_442892046_H8uk2FEg3hlv9bb4zu8fDk4A88VTVL8J.jpg"
LIST = [
    {
        "name": "Default",
        "quantity": 1,
        "unit_cost": 1,
        "description": "item description"
    }
]  

class GenInvoice:
    def __init__(self,frm=FROM,currency="INR",notes=NOTES,terms=TERMS,url=URL,logo=LOGO) -> None:
        self.frm = frm 
        self.currency = currency
        self.notes= notes
        self.terms = terms
        self.url = url
        self.logo = logo
    def downloadInvoice(self,to:str,address:str,order_no:str,amount_paid:int,discount=0,tax:float=0,shipping:int=0,items:list=LIST):
        current_date = datetime.now().date().isoformat()
        payload = {
                    'logo': self.logo,
                    'from': self.frm,
                    'to': to,
                    "ship_to": address,
                    "number": order_no,
                    "currency": self.currency,
                    "date": current_date,
                    "discounts": discount,
                    "tax": tax,
                    "shipping": shipping,
                    "amount_paid": amount_paid,
                    "notes": self.notes,
                    "terms": self.terms,
                    "items": items,
                    "fields": {
                                "tax": "%",
                                "discounts": True,
                                "shipping": True
                              },
                  }
        response = requests.post(URL, json=payload)
        if response.status_code == 200:
            self.invoice = f"Downloads/{order_no}-{to}-{current_date}.pdf"
            with open(self.invoice, 'wb') as f:
                f.write(response.content)
            return response.status_code,self.invoice
        else:
            return response.status_code
    def deleteInvoice(self):
        if path.exists(self.invoice):
            remove(self.invoice)
            return True
        else:
            return False          

# array = [
#     {
#         "name": "Erase",
#         "quantity": 2,
#         "unit_cost": 5,
#         "description": "Absara eraser"
#     },
#     {
#         "name": "Kurkure",
#         "quantity": 5,
#         "unit_cost": 20
#     },
#     {
#         "name": "burger",
#         "quantity": 2,
#         "unit_cost": 100
#     },
# ]

# inv = GenInvoice()
# inv.downloadInvoice(to="amitabh",address="shimla bemloi 171009",order_no="f435v34",amount_paid=200,discount=20,tax=10,shipping=50,items=array)
# inv.deleteInvoice()