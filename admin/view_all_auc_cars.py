import flask as fl
import tools.db_api as db
from tools.auth import AuthApi
import logging as log
from random import choice
from datetime import datetime, timedelta, timezone

bp = fl.Blueprint("bp_admin_auc", __name__)


def pretty_num(price):
    return f"{price:_}".replace("_", " ")


@bp.route("/get_auc_cars")
def get_auc_cars():
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
        return res

    cars = []

    if fl.request.args.get("sortby") != None:
        sortby = fl.request.args.get("sortby")
    else:
        sortby = "mile"

    try:
        conn = db.DBConnection()
        user_role = conn.get_user_perms(user['message']['id'])
        
        if user_role['Allow_ext_car_view'] == True:
            cars_db = conn.get_auc_car(closed=True)
        else:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
        

        for car in cars_db:
            car_new = {}
            car_new["id"] = car["id"]
            car_new["car_brand"] = car["brand"]
            car_new["car_model"] = car["model"]
            car_new["car_year"] = car["year"]
            car_new["main_info"] = (
                f'{pretty_num(car["mileage"])} км, {pretty_num(car["hp"])} л.с., {car["fuel_type"]}'
            )
            car_new["addit_info"] = f'{car["transmission"]}, {car["body_type"]}'
            car_new["start_price"] = pretty_num(car["start_price"])
            car_new["car_img"] = (
                f'../cars_imgs/auc_cars/{car["id"]}/{conn.get_auc_car_pics(car["id"])[0]["pic_name"]}'
            )
            curr_price = conn.get_auc_car_price(car_new["id"])
            car_new["close_time"] = car["close_time"].strftime("%d.%m.%Y %H:%M")
            car_new["current_price"] = pretty_num(car["start_price"]+(curr_price if curr_price != None else 0))
            cars.append(car_new)

        conn.close()

    except Exception as e:
        log.error(f"AUC_VIEW: {e}")
        return fl.render_template("500.html")

    return fl.render_template("auc_cars.html", cars=cars, user_role=user_role)


@bp.route("/view_auc_cars")
def view_auc_cars():
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        return fl.redirect(f"/?auth=1")
    try:
        conn = db.DBConnection()
        user_role = conn.get_user_perms(user['message']['id'])
        if user_role['Allow_ext_car_view'] == False:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
    except Exception as e:
        log.error(e)
        fl.abort(500)
    finally:
        conn.close()

    return fl.render_template("view_auc_cars.html", active_deals='')