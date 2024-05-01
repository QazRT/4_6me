import flask as fl
import tools.db_api as db
from tools.auth import AuthApi
import logging as log
from random import choice
from datetime import datetime, timedelta, timezone

bp = fl.Blueprint("bp_sale", __name__)

def pretty_num(price):
    return f"{price:_}".replace('_',' ')

@bp.route("/get_sale_cars")
def get_sale_cars():
    user = AuthApi.is_loggged_in()
    if user['status'] == False:
        res = fl.make_response(fl.redirect(f"/?auth=1&sale=1"), 403)
        return res
    
    
    cars = []
    
    if fl.request.args.get("sortby") != None:
        sortby = fl.request.args.get("sortby")
    else:
        sortby = "mile"
        
    try:
        conn = db.DBConnection()
        cars_db = conn.get_trade_car(sortby=sortby)
                
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
        
        conn.close()
    
    except Exception as e:
        log.error(e)
        return fl.render_template("500.html")
    
    return fl.render_template("sale_cars.html", cars=cars)


@bp.route("/trade_car")
@bp.route("/trade_car/")
@bp.route("/sale")
def sale():
    user = AuthApi.is_loggged_in()
    if user['status'] == False:
        return fl.redirect(f"/?auth=1&sale=1")
    
    try:
        conn = db.DBConnection()
        conn.executeonce("SELECT COUNT(id) FROM \"Trade_cars\" WHERE status=1")
        active_deals = conn.fetchone()["count"]
        conn.close()
    
    except Exception as e:
        log.error(e)
        fl.abort(500)
    
    return fl.render_template("sale.html", active_deals=active_deals)
    