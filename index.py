import flask as fl
import tools.db_api as db
import logging as log
from datetime import datetime, timedelta, timezone

bp = fl.Blueprint("bp_file1", __name__)

def pretty_price(price):
    return f"{price:_}".replace('_',' ')

@bp.route("/get_2close_time/<car_id>")
def get_2close_time(car_id):
    conn = db.DBConnection()
    conn.executeonce("SELECT * FROM \"Auction_cars\" WHERE id=%(id)s", {"id": car_id})
    auc_car = dict(conn.fetchone())
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
    car_new["price"] = pretty_price(car["price"])
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
        conn.executeonce("SELECT COUNT(action) FROM public.\"Auction_history\" WHERE car_id=%(car_id)s GROUP BY action, car_id HAVING action='Bet';", {"car_id": auc_car["id"]})
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
        auc_car_new["start_price"] = pretty_price(auc_car["start_price"])
        auc_car_new["current_price"] = pretty_price(auc_car["start_price"]+(curr_price if curr_price!= None else 0))
        auc_car_new["auc_car_img"] = f'../cars_imgs/auc_cars/{auc_car["id"]}/{conn.get_auc_car_pics(auc_car["id"])[0]["pic_name"]}'
        
    
    
        for car in cars_db:
            car_new = {}
            car_new["id"] = car["id"]
            car_new["car_brand"] = car["brand"]
            car_new["car_model"] = car["model"]
            car_new["car_year"] = car["year"]
            car_new["main_info"] = f'{car["mileage"]}км, {car["hp"]}лс, {car["fuel_type"]}'
            car_new["addit_info"] = f'{car["transmission"]}, {car["body_type"]}'
            car_new["price"] = pretty_price(car["price"])
            car_new["car_img"] = f'../cars_imgs/trade_cars/{car["id"]}/{conn.get_trade_car_pics(car["id"])[0]["pic_name"]}'
            cars.append(car_new)
        
    except Exception as e:
        log.error(f"INDEX (/): {e}")
        
    return fl.render_template("home.html", cars=cars, **auc_car_new, auction_count=auction_count)

@bp.route("/test", methods=["GET", "POST"])
def test():
    conn = db.DBConnection()
    methods = list(filter(lambda x: not x.startswith("_"), dir(conn)))
    if fl.request.method == "POST":
        select = fl.request.form.get("test_select")
        args = fl.request.form.get("args")
        log.info(f"conn.{select}({args})")
        name = eval(f"conn.{select}({args})")
        # name = select
    else:
        # conn.add_auc_car(body_type="Седан")
        name = "world"
    return fl.render_template("test.html", name=name, option=methods)