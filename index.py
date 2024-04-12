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
    auc_car = conn.get_auc_car(id=car_id)
    return f'{int(cl_time := (auc_car["close_time"]-datetime.now(tz=timezone(timedelta(hours=3.0)))).total_seconds())//86400}д {int(cl_time-(cl_time//86400)*86400)//3600}ч {int(cl_time-(cl_time//86400)*86400-((cl_time-(cl_time//86400)*86400)//3600)*3600)//60}м {int(cl_time-(cl_time//86400)*86400-((cl_time-(cl_time//86400)*86400)//3600)*3600-(((cl_time-(cl_time//86400)*86400)//3600)*3600)//60)%60}c'


@bp.route("/")
def home():
    cars = []

    conn = db.DBConnection()
    cars_db = conn.get_trade_car()

    try:
        auc_car = conn.get_auc_car(limit = 1)
        if len(auc_car) == 0:
            auc_car = conn.get_auc_car(limit = 1, closed=True)[0]
        else:
            auc_car = auc_car[0]
        
        auc_car_new = {}
        conn.executeonce("SELECT COUNT(action) FROM public.\"Auction_history\" WHERE car_id=%(car_id)s GROUP BY action, car_id HAVING action='Bet';", {"car_id": auc_car["id"]})
        part_count = conn.fetchone()
        
        conn.executeonce("SELECT COUNT(*) FROM \"Auction_cars\" where id in (SELECT car_id FROM \"Auction_history\" WHERE action != 'Sold' AND action != 'Hide') AND close_time > CURRENT_TIMESTAMP")
        auction_count = 0 if (tmp := conn.fetchone()["count"]) == None else tmp
        auc_car_new["auc_car_id"] = auc_car["id"]
        auc_car_new["auc_car_brand"] = auc_car["brand"]
        auc_car_new["auc_car_model"] = auc_car["model"]
        auc_car_new["auc_car_year"] = auc_car["year"]
        auc_car_new["auc_car_trans"] = auc_car["transmission"]
        # auc_car_new["auc_car_until_close_time"] = f'{int(cl_time := (auc_car["close_time"]-datetime.now(tz=timezone(timedelta(hours=3.0)))).total_seconds())//86400}д {int(cl_time-(cl_time//86400)*86400)//3600}ч {int(cl_time-(cl_time//86400)*86400-((cl_time-(cl_time//86400)*86400)//3600)*3600)//60}м'
        auc_car_new["auc_car_close_date"] = auc_car["close_time"].strftime("%d.%m.%Y %H:%M")
        auc_car_new["participants_count"] = 0 if part_count == None else part_count["count"]
        auc_car_new["start_price"] = pretty_price(auc_car["start_price"])
        auc_car_new["current_price"] = pretty_price(auc_car["start_price"]+conn.get_auc_car_price(auc_car["id"]))
        auc_car_new["auc_car_img"] = f'../cars_imgs/auc_cars/{auc_car["id"]}/{conn.get_auc_car_pics(auc_car["id"])[0]["pic_name"]}'
        
    
    
        for car in cars_db:
            car_new = {}
            car_new["car_brand"] = car["brand"]
            car_new["car_model"] = car["model"]
            car_new["car_year"] = car["year"]
            car_new["main_info"] = f'{car["mileage"]}км, {car["hp"]}лс, {car["fuel_type"]}'
            car_new["addit_info"] = f'{car["transmission"]}, {car["body_type"]}'
            car_new["price"] = pretty_price(car["price"])
            car_new["car_img"] = f'../cars_imgs/trade_cars/{car["id"]}/{conn.get_trade_car_pics(car["id"])[0]["pic_name"]}'
            cars.append(car_new)
        
    except Exception as e:
        log.error(e)
        
    return fl.render_template("home.html", cars=cars, **auc_car_new, auction_count=auction_count)


@bp.route("/hometest")
def hometest():
    cars = [
        {
            "car_brand": "Toyota0",
            "car_model": "Corolla",
            "car_year": "2023",
            "main_info": "120 км, 125лс, Бензин",
            "addit_info": "Автомат",
            "price": 35000000,
            "car_img": "../images/b1a16b0c01ec4855f3cf78989ecbd204a3be2cf8.png",
        },
        {
            "car_brand": "Toyota1",
            "car_model": "Corolla",
            "car_year": "2023",
            "main_info": "120 км, 125лс, Бензин",
            "addit_info": "Автомат",
            "price": 35000000,
            "car_img": "../images/b1a16b0c01ec4855f3cf78989ecbd204a3be2cf8.png",
        },
        {
            "car_brand": "Toyota2",
            "car_model": "Corolla",
            "car_year": "2023",
            "main_info": "120 км, 125лс, Бензин",
            "addit_info": "Автомат",
            "price": 35000000,
            "car_img": "../images/b1a16b0c01ec4855f3cf78989ecbd204a3be2cf8.png",
        },
        {
            "car_brand": "Toyota3",
            "car_model": "Corolla",
            "car_year": "2023",
            "main_info": "120 км, 125лс, Бензин",
            "addit_info": "Автомат",
            "price": 35000000,
            "car_img": "../images/b1a16b0c01ec4855f3cf78989ecbd204a3be2cf8.png",
        },
        # {"car_brand": "Toyota4", "car_model": "Corolla", "car_year": "2023", "main_info": "120 км, 125лс, Бензин", "addit_info": "Автомат", "price": 35000000, "car_img": "../images/b1a16b0c01ec4855f3cf78989ecbd204a3be2cf8.png"},
        # {"car_brand": "Toyota5", "car_model": "Corolla", "car_year": "2023", "main_info": "120 км, 125лс, Бензин", "addit_info": "Автомат", "price": 35000000, "car_img": "../images/b1a16b0c01ec4855f3cf78989ecbd204a3be2cf8.png"},
    ]
    return fl.render_template("home_test.html", cars=cars)


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


@bp.route("/test_button")
def test_button():
    return fl.redirect("/test")
