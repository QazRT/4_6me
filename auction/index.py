import flask as fl
import tools.db_api as db
from tools.auth import AuthApi
import logging as log
from random import choice
from datetime import datetime, timedelta, timezone

bp = fl.Blueprint("bp_file2", __name__)

def pretty_num(price):
    return f"{price:_}".replace('_',' ')

@bp.route("/get_car_card")
def auction_get_car():    
    
    user = AuthApi.is_loggged_in()
    carid = fl.request.args.get('carid')
    if user['status'] == False:
        if carid != None:
            res = fl.make_response(fl.redirect(f"/?auth=1&auc={carid}"), 403)
        else:
            res = fl.make_response(fl.redirect(f"/?auth=1&auc=-1"), 403)
            
        return res
            
    
    conn = db.DBConnection()

    try:
        if fl.request.cookies.get('prevcars') != None and fl.request.cookies.get('prevcars') != '':
            prevcars = list(map(str, fl.request.cookies.get('prevcars').split(',')))
        else:
            prevcars = []
        if fl.request.args.get('carid') == None or fl.request.args.get('carid') == 'null':
            previd = fl.request.args.get('prevcarid')
            
                                                
            log.error(prevcars)
            
            if previd != None:
                prevcars.append(previd)
                
            conn.executeonce("SELECT COUNT(*) FROM \"Auction_cars\" where (id in (SELECT car_id FROM \"Auction_history\" WHERE ACTION != 'Sold' AND ACTION != 'Hide') OR id not in (SELECT car_id FROM \"Auction_history\")) AND CLOSE_TIME > CURRENT_TIMESTAMP")
            auction_count = 0 if (tmp := conn.fetchone()["count"]) == None else tmp
            if len(prevcars) == auction_count:
                prevcars = [previd]
            
            if prevcars != []:
                auc_car = conn.get_auc_car(where = f'"Auction_cars".id NOT IN ({",".join(map(str, prevcars))})' if str(previd).isdigit() else True)
            else:
                auc_car = conn.get_auc_car()
                                                                
            if len(auc_car) == 0:
                auc_car = conn.get_auc_car(limit = 1, closed=True)
            auc_car = choice(auc_car)
            
        else:
            auc_car = conn.get_auc_car(id=fl.request.args.get('carid'))

        
        conn.executeonce("SELECT COUNT(action) FROM public.\"Auction_history\" WHERE car_id=%(car_id)s GROUP BY action, car_id HAVING action='Bet';", {"car_id": auc_car["id"]})
        part_count = conn.fetchone()
        curr_price = conn.get_auc_car_price(auc_car["id"])
        auc_car["mileage"] = pretty_num(auc_car["mileage"])
        auc_car["part_count"] = 0 if part_count == None else part_count["count"]
        auc_car["close_time"] = auc_car["close_time"].strftime("%d.%m.%Y %H:%M")
        auc_car["current_price"] = pretty_num(auc_car["start_price"]+(curr_price if curr_price != None else 0))
        auc_car["start_price"] = pretty_num(auc_car["start_price"])
        auc_car["fuel_type"] = auc_car["fuel_type"] if auc_car["fuel_qual"] == None else f'{auc_car["fuel_type"]} (АИ-{auc_car["fuel_qual"]})'

        imgs = list(i["pic_name"] for i in conn.get_auc_car_pics(auc_car["id"]))
        

            
    except Exception as e:
        log.error(e)
        fl.abort(500)

        
    res = fl.make_response(fl.render_template("auction_car.html", **auc_car, imgs=imgs))
    res.set_cookie("prevcars", ','.join(map(str, prevcars)))
    
    return res

@bp.route("/bet_car/<carid>", methods=['POST'])
def bet_car(carid):
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        return fl.redirect(f"/?auth=1")
    
    if carid.isdigit() == False:
        return fl.render_template("404.html")
           
    try:
        conn = db.DBConnection()
               
        if int(fl.request.form.get('userprice')) - int(conn.get_auc_car_current_price(car_id=carid)) >= 1000:
            conn.set_auc_car_status(car_id=carid, user_id=user["message"]["id"],
                                        action=db.AucActions.BET,
                                        action_info=str(int(fl.request.form.get('userprice')) - int(conn.get_auc_car_current_price(car_id=carid))))
        
        else:
            return 'False'
        
    except Exception as e:
        log.error(f"Bet_Car: {e}")
        return fl.render_template("500.html")
    finally:
        conn.close()
        
    return 'True'
    

@bp.route("/auction")
def auction_index():
    user = AuthApi.is_loggged_in()
    carid = fl.request.args.get('carid')
    if user['status'] == False:
        if carid != None:
            res = fl.make_response(fl.redirect(f"/?auth=1&auc={carid}"))
        else:
            res = fl.make_response(fl.redirect(f"/?auth=1&auc=-1"))
            
        
        return res
    
    return fl.render_template("auction.html")
