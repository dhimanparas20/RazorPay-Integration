from flask import Flask,request,make_response,render_template,send_file,after_this_request
from flask_restful import Api, Resource
from flask_session import Session
from datetime import datetime
from genInvoice import GenInvoice
import configparser as cp
import razorpay
from os import system

system("clear")

# Read configuration from file
cfg = cp.ConfigParser()
cfg.read('config.conf')

# READ VARIABLES from config file
DEBUG = True if cfg['FLASK']['DEBUG'] == "true" or cfg['FLASK']['DEBUG'] == "True"  else False
HOST = cfg['FLASK']['HOST']     # Host address of Server "127.0.0.1"   
PORT = int(cfg['FLASK']['SERVER_PORT'])  # Port for this server to run 5000
SECRET_KEY = cfg['FLASK']['FLASK_SECRET_KEY']  #Secure Session Secret Key
RZPAY_ID = cfg['RAZOR_PAY']['ID']
RZPAY_CLIENT = cfg['RAZOR_PAY']['SECRET']
PERDEVICE_COST = int(cfg['RAZOR_PAY']['PERDEVICE_COST'])  # Regitration cost per Token
CURRENCY = cfg['RAZOR_PAY']['CURRENCY'] 
COMPANY_NAME = cfg['RAZOR_PAY']['COMPANY_NAME'] 
ADDRESS = cfg['RAZOR_PAY']['ADDRESS']  

class RazorPay:
    def __init__(self) -> None:
        self.client = razorpay.Client(auth=(RZPAY_ID, RZPAY_CLIENT)) #Razor pay OBJECT
    def genOrder(self, data: dict,description:str="Payment of Services") -> [dict, bool]:
        self.data = data
        self.payment = self.client.order.create(data=self.data)
        if self.payment != {}:
            self.payment['RZPAY_ID'] = RZPAY_ID
            self.payment['COMPANY_NAME'] = COMPANY_NAME
            self.payment['ADDRESS'] = ADDRESS
            self.payment['DESCRIPTION'] = description
            return self.payment
        else:
            return False
    def verifyOrder(self, data: dict) -> bool:
        response = self.client.utility.verify_payment_signature({  #verify tranxaction
            'razorpay_order_id': data["razorpay_order_id"],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data["razorpay_signature"]
            })
        return response
    def getPyament(self) -> dict:
        return self.payment

def genTimeStamp() -> int:
    # Current date and time
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%Y%m%d%H%M%S")
    return int(timestamp)    

# Objects and imprtant variables
app = Flask(__name__)
api = Api(app)
app.secret_key = SECRET_KEY
app.config['SECRET_KEY'] = SECRET_KEY
Session(app)
rzp = RazorPay()
inv = GenInvoice()

# Configure session to use filesystem
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

# Configure the session cookie settings
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_SECURE'] = True  # Make sure secure cookies are enabled


class Home(Resource):
    def get(self):
        return make_response(render_template("index.html"))
    def post(self):
        data = request.form.to_dict()
        qty = int(data['qty'])
        order = { 
                "amount": qty*PERDEVICE_COST*100, 
                "currency": CURRENCY, 
                "receipt": str(genTimeStamp()),
                "notes":{
                    "name":"Sample Name",
                    "contact":"1234567890",
                    "email":"abc@mail,com"
                    }   
                } 
        payment = rzp.genOrder(data=order)
        return payment
    
class Verify(Resource):
    def post(self):
        data = request.form.to_dict()  #data received from post req*
        response = rzp.verifyOrder(data)
        if response == True:
            payment = rzp.getPyament()
            redirectURL = f"/getreceipt?razorpay_payment_id={data['razorpay_payment_id']}&razorpay_order_id={data['razorpay_order_id']}&Name={payment['notes']['name']}&Contact={payment['notes']['contact']}&Amount={payment['amount']/100}&Email={payment['notes']['email']}&Receipt={payment['receipt']}"
            return redirectURL
        else:
            return ({"msg":False}) 

# generates receipt  "/getreceipt"
class GetReceipt(Resource):
    def get(self):
        data = request.args.to_dict()
        items = [
                    {
                        "name": "Erase",
                        "quantity": 2,
                        "unit_cost": 5,
                        "description": "Absara eraser"
                    },
                    {
                        "name": "Kurkure",
                        "quantity": 5,
                        "unit_cost": 20
                    },
                    {
                        "name": "burger",
                        "quantity": 2,
                        "unit_cost": 100
                    },
                ]
        lst = {
            "to":data['Name'],
            "address":"Default address",
            "order_no": data['razorpay_order_id'],
            "amount_paid":data['Amount'],
            "discount":0,
            "tax":0,
            "shipping":0,
            "items":items
        }
        status_code,resp = inv.downloadInvoice(to=lst['to'],address=lst['address'],order_no=lst['order_no'],amount_paid=lst['amount_paid'],discount=lst['discount'],tax=lst['tax'],shipping=lst['shipping'],items=lst['items'])

        if status_code == 200:
            try: 
                return send_file(resp,as_attachment=True,mimetype='application/pdf'
            )
            finally:
                inv.deleteInvoice()  
            
        else:
            return {'error': 'Failed to generate receipt'}, 500        
        

# All the Routes
api.add_resource(Home, '/')
api.add_resource(Verify, '/verify') 
api.add_resource(GetReceipt, '/getreceipt')


if __name__ == '__main__':
    app.run(debug=DEBUG,port=PORT,host=HOST,threaded=True)
         
