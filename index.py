import flask as fl
from flask_mail import Message
import tools.db_api as db
import logging as log
from tools.auth import AuthApi
from datetime import datetime, timedelta, timezone


bp = fl.Blueprint("bp_file1", __name__)

def pretty_num(price):
    return f"{price:_}".replace('_',' ')

@bp.route("/get_2close_time/<car_id>")
def get_2close_time(car_id):
    conn = db.DBConnection()
    conn.executeonce("SELECT * FROM \"Auction_cars\" WHERE id=%(id)s", {"id": car_id})
    auc_car = dict(conn.fetchone())
    conn.close()
    return f'{int(cl_time := (auc_car["close_time"]-datetime.now(tz=timezone(timedelta(hours=3.0)))).total_seconds())//86400}д {int(cl_time-(cl_time//86400)*86400)//3600}ч {int(cl_time-(cl_time//86400)*86400-((cl_time-(cl_time//86400)*86400)//3600)*3600)//60}м {int(cl_time-(cl_time//86400)*86400-((cl_time-(cl_time//86400)*86400)//3600)*3600-(((cl_time-(cl_time//86400)*86400)//3600)*3600)//60)%60}c'

@bp.route("/get_trade_car")
def get_trade_car():
    conn = db.DBConnection()
    car = conn.get_trade_car(id=fl.request.args.get('carid'))
    car_new = {}
    car_new["id"] = car["id"]
    car_new["car_brand"] = car["brand"]
    car_new["car_model"] = car["model"]
    car_new["car_year"] = car["year"]
    car_new["main_info"] = f'{car["mileage"]}км, {car["hp"]}лс, {car["fuel_type"]}'
    car_new["addit_info"] = f'{car["transmission"]}, {car["body_type"]}'
    car_new["price"] = pretty_num(car["price"])
    car_new["car_img"] = f'../cars_imgs/trade_cars/{car["id"]}/{conn.get_trade_car_pics(car["id"])[0]["pic_name"]}'
    return fl.render_template("get_trade_car_on_home.html", tmp=fl.request.args.get('tmp'), car=car_new, loop0=fl.request.args.get('loop0'))



@bp.route("/")
def home():
    cars = []

    conn = db.DBConnection()
    cars_db = conn.get_trade_car(limit=8)

    try:
        auc_car = conn.get_auc_car(limit = 1)
        if len(auc_car) == 0:
            auc_car = conn.get_auc_car(limit = 1, closed=True)[0]
        else:
            auc_car = auc_car[0]
        
        auc_car_new = {}
        conn.executeonce("SELECT COUNT(action) FROM (SELECT DISTINCT user_id, action FROM public.\"Auction_history\" WHERE car_id=%(car_id)s) GROUP BY action HAVING action='Bet'", {"car_id": auc_car["id"]})
        part_count = conn.fetchone()
        
        conn.executeonce("SELECT COUNT(*) FROM \"Auction_cars\" where (id in (SELECT car_id FROM \"Auction_history\" WHERE ACTION != 'Sold' AND ACTION != 'Hide') OR id not in (SELECT car_id FROM \"Auction_history\")) AND CLOSE_TIME > CURRENT_TIMESTAMP")
        auction_count = 0 if (tmp := conn.fetchone()["count"]) == None else tmp
        curr_price = conn.get_auc_car_price(auc_car["id"])
        auc_car_new["auc_car_id"] = auc_car["id"]
        auc_car_new["auc_car_brand"] = auc_car["brand"]
        auc_car_new["auc_car_model"] = auc_car["model"]
        auc_car_new["auc_car_year"] = auc_car["year"]
        auc_car_new["auc_car_trans"] = auc_car["transmission"]
        # auc_car_new["auc_car_until_close_time"] = f'{int(cl_time := (auc_car["close_time"]-datetime.now(tz=timezone(timedelta(hours=3.0)))).total_seconds())//86400}д {int(cl_time-(cl_time//86400)*86400)//3600}ч {int(cl_time-(cl_time//86400)*86400-((cl_time-(cl_time//86400)*86400)//3600)*3600)//60}м'
        auc_car_new["auc_car_close_date"] = auc_car["close_time"].strftime("%d.%m.%Y %H:%M")
        auc_car_new["participants_count"] = 0 if part_count == None else part_count["count"]
        auc_car_new["start_price"] = pretty_num(auc_car["start_price"])
        auc_car_new["current_price"] = pretty_num(auc_car["start_price"]+(curr_price if curr_price!= None else 0))
        auc_car_new["auc_car_img"] = f'../cars_imgs/auc_cars/{auc_car["id"]}/{conn.get_auc_car_pics(auc_car["id"])[0]["pic_name"]}'
        
    
    
        for car in cars_db:
            car_new = {}
            car_new["id"] = car["id"]
            car_new["car_brand"] = car["brand"]
            car_new["car_model"] = car["model"]
            car_new["car_year"] = car["year"]
            car_new["main_info"] = f'{pretty_num(car["mileage"])} км, {pretty_num(car["hp"])} л.с., {car["fuel_type"]}'
            car_new["addit_info"] = f'{car["transmission"]}, {car["body_type"]}'
            car_new["price"] = pretty_num(car["price"])
            car_new["car_img"] = f'../cars_imgs/trade_cars/{car["id"]}/{conn.get_trade_car_pics(car["id"])[0]["pic_name"]}'
            cars.append(car_new)
        
    except Exception as e:
        log.error(f"INDEX (/): {e}")
        fl.abort(500)
        
    return fl.render_template("home.html", cars=cars, **auc_car_new, auction_count=auction_count)

@bp.route("/error/<error_id>")
def error_example(error_id):
    if error_id in ['403', '404', '500']:
        return fl.render_template(f"{error_id}.html")
    else:
        return fl.render_template(f"403.html")

@bp.route("/auc_congrat/<car_id>")
def auc_congrat(car_id = None):
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        return fl.redirect(f"/?auth=1")
       
    if car_id.isdigit() == False:
        return fl.render_template("404.html")
    
    try:
        conn = db.DBConnection()
        price = conn.get_auc_car_current_price(car_id=int(car_id))
        log.error(price)
    except Exception as e:
        log.error(e)
        return fl.render_template("500.html")
    finally:
        conn.close()
        
    return fl.render_template("auc_buy_msg.html", curr_price=price+1000)

@bp.route("/congrat/<carid>")
def congrat(carid):
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        return fl.redirect(f"/?auth=1")
    
    if carid.isdigit() == False:
        return fl.render_template("404.html")
           
    try:
        conn = db.DBConnection()
        
        conn.executeonce("SELECT status FROM public.\"Trade_cars\" WHERE id = %(id)s", {"id": carid})
        status = conn.fetchone()["status"]
        
        if status == 1:
            conn.executeonce("""UPDATE public."Trade_cars" SET status=2 WHERE id=%(car_id)s""", {"car_id": carid})
            emsg = Message("Запрос на покупку авто", recipients=['managers@nobless-oblige.ru'])
            emsg.html = fl.render_template("buy_mail.html", user=user['message'], carid=carid)
            
        else:
            return fl.render_template("403.html")

    except Exception as e:
        log.error(f"Bet_Car: {e}")
        return fl.render_template("500.html")
    finally:
        conn.close()
    
    return fl.render_template("buy_msg.html")

@bp.route("/ready_auc_congrat")
def ready_auc_congrat():
    return fl.render_template("ready_auc_congrat.html")
