import flask as fl
import tools.db_api as db
from tools.auth import AuthApi
import logging as log
from random import choice
from datetime import datetime, timedelta, timezone

bp = fl.Blueprint("bp_car_details", __name__)

def pretty_num(price):
    return f"{price:_}".replace('_',' ')

@bp.route("/trade_car/<car_id>")
def trade_car(car_id):
    user = AuthApi.is_loggged_in()
    if user['status'] == False:
        return fl.redirect(f"/?auth=1&trade_car={car_id}")
    
    try:
        conn = db.DBConnection()
        
        car = conn.get_trade_car(id=int(car_id))
        if car == None:
            return fl.render_template("404.html")
        
        car['price'] = pretty_num(car['price'])
        car['hp'] = pretty_num(car['hp'])
        car['mileage'] = pretty_num(car['mileage'])
        imgs = list(i["pic_name"] for i in conn.get_trade_car_pics(car_id=car_id))
        
        
        conn.close()
    except Exception as e:
        log.error(e)
        return fl.render_template("500.html")
    
    return fl.render_template("trade_car_details.html", **car, imgs=imgs)
