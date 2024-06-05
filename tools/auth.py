import flask as fl
import tools.db_api as db
import logging as log
from datetime import datetime, timedelta, timezone
import hashlib
import base64 as bs64

bp = fl.Blueprint("bp_file3", __name__)

def pretty_phone(phone) -> str:
    if len(phone) != 11 or phone.isdigit() == False:
        return "8 (800) 555-35-35"
    
    return f"8 ({phone[1:4]}) {phone[4:7]}-{phone[7:9]}-{phone[9:11]}"

def pretty_num(price):
    return f"{price:_}".replace('_',' ')

class AuthApi:    
    @staticmethod
    def check_user(email, password):
        try:
            conn = db.DBConnection()
            passkey = hashlib.sha256(str(email+password).encode()).hexdigest()            
            res = conn.get_user(email=email, passkey=passkey)
            conn.close()
            
            if res['exists'] == False:
                return {"status": False, "message": f"User with this credentials does not exist"}
            else:
                return {"status": True, "message": res}
            
        except Exception as e:
            log.error(e)
            return {"status": False, "message": f"Error while checking user. Check logs for more information"}

    @staticmethod
    def reg_user(name, surname, phone_number,
                    birthday, password, email):
        try:
            conn = db.DBConnection()
            conn.executeonce("SELECT EXISTS(SELECT id FROM \"Users\" WHERE \"Email\"=%(email)s)",
                             {"email": email})
            if dict(conn.fetchone())['exists']:
                return {"status": False, "message": f"User with email {email} already exists"}
                    
            
            passkey = hashlib.sha256(str(email+password).encode()).hexdigest()
            res = conn.add_user(name, surname, phone_number, birthday, passkey, email)
            conn.close()
            if res['status'] == False:
                return {"status": False, "message": f"Error while adding user. Check logs for more information"}
            
            return {"status": True, "message": {"Email": email, "Passkey": passkey}}
            
        except Exception as e:
            log.error(e)
            return {"status": False, "message": "Error while adding user. Check logs for more information"}
    
    @staticmethod
    def is_loggged_in():
        try:
            user_token = fl.request.cookies.get('token')
            if user_token == None:
                return {"status": False, "message": f"You are not logged in"}
            
            email, passkey = bs64.b64decode(user_token.encode()).decode().split(' ')
            conn = db.DBConnection()
            res = conn.get_user(email=email, passkey=passkey)
            # res = AuthApi.check_user(email=email, password=passkey)
            conn.close()
            
            # log.error(res)
            
            if res['exists'] == False:
                return {"status": False, "message": f"User with this credentials does not exist"}
            
            return {"status": True, "message": res}
            
        except Exception as e:
            log.error(e)
            return {"status": False, "message": f"Error while operating. Check logs for more information"}
    
    
    

@bp.route("/register", methods=["POST"])
def register():
    try:
        name = fl.request.form.get("name")
        surname = fl.request.form.get("surname")
        phone_number = fl.request.form.get("phone")
        birthday = "01.01.1990"
        password = fl.request.form.get("password")
        email = fl.request.form.get("email")
        
        
        res = AuthApi.reg_user(name, surname, phone_number, birthday, password, email)
        # log.warn(f"{res['message']['Email']} {res['message']['Passkey']}".encode())
        if res['status'] == False:
            return 'False'
        
        res1 = fl.make_response('True')
        res1.set_cookie("token", bs64.b64encode(f"{res['message']['Email']} {res['message']['Passkey']}".encode()).decode(), max_age=86400)
        return res1

    except Exception as e:
        log.error(e)
        fl.abort(500)


@bp.route("/login", methods=["POST"])
def login():
    try:
        res = AuthApi.check_user(email=fl.request.form.get("email"), password=fl.request.form.get("password"))
        if res['status'] == False:
            return 'False'
        
        res1 = fl.make_response('True')
        res1.set_cookie("token", bs64.b64encode(f"{res['message']['Email']} {res['message']['Passkey']}".encode()).decode(), max_age=86400)
        return res1
    
    except Exception as e:
        log.error(e)
        return 'False'
                

@bp.route("/auth")
def get_auth_window():
    user = AuthApi.is_loggged_in()
    if user['status'] == False:
        return fl.render_template("auth_window.html")
    
    else:
        try:
            conn = db.DBConnection()
            conn.executeonce("""
                            SELECT car_id FROM "Auction_cars" JOIN "Auction_history" ON
                            "Auction_cars".id = "Auction_history".car_id
                            WHERE "Auction_history".user_id=%(user_id)s AND "Auction_history".action='Bet'
                            AND NOT EXISTS(SELECT id FROM "Auction_history" WHERE "Auction_history".action='Sold' 
                                AND "Auction_history".car_id="Auction_cars".id)
                            GROUP BY "Auction_history".car_id
                            """, {"user_id": user['message']['id']})
            process_cars_ids = conn.fetchall()
            process_cars = []
            
            if len(process_cars_ids) != 0:
                for i in process_cars_ids:
                    process_cars.append(conn.get_auc_car(id=i['car_id']))
                
                for car in process_cars:
                    conn.executeonce("""SELECT timestamp FROM "Auction_history" WHERE
                                                        car_id = %(car_id)s 
                                                        AND action = 'Bet' ORDER BY timestamp DESC LIMIT 1""",
                                             {"car_id": car['id']})
                    car['timestamp'] = dict(conn.fetchone())['timestamp'].strftime("%d.%m.%Y")
                    car['curr_price'] = pretty_num(conn.get_auc_car_current_price(car_id=car['id']))
                
            conn.executeonce("""
                             SELECT car_id FROM "Auction_cars" JOIN "Auction_history" ON
                            "Auction_cars".id = "Auction_history".car_id
                            WHERE "Auction_history".user_id=%(user_id)s AND "Auction_history".action='Sold'
                            GROUP BY "Auction_history".car_id
                            """, {"user_id": user['message']['id']})

            auc_cars_ids = conn.fetchall()
            auc_cars = []
            
            if len(auc_cars_ids) != 0:
                for i in auc_cars_ids:
                    auc_cars.append(conn.get_auc_car(id=i['car_id']))
                
                for car in auc_cars:
                    conn.executeonce("""SELECT timestamp FROM "Auction_history" WHERE
                                    car_id = %(car_id)s 
                                    AND action = 'Sold' ORDER BY timestamp DESC LIMIT 1""",
                            {"car_id": car['id']})
                    car['timestamp'] = dict(conn.fetchone())['timestamp'].strftime("%d.%m.%Y")
                    car['curr_price'] = pretty_num(conn.get_auc_car_current_price(car_id=car['id']))
            
            for car in auc_cars:
                car['curr_price'] = pretty_num(conn.get_auc_car_current_price(car_id=car['id']))
                
            user_perms = conn.get_user_perms(user['message']['id'])
        
        except Exception as e:
            log.error(e)
            return fl.render_template("500.html")

        finally:
            conn.close()
        
        return fl.render_template("profile_window.html", auc_cars=auc_cars, user_perms=user_perms, proc_cars=process_cars, email=user['message']['Email'], name=user['message']['Name'], 
                                  surname=user['message']['Surname'], phone_number=pretty_phone(user['message']['Phone_number']))
        
    # return fl.redirect("/auction")