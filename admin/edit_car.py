﻿import flask as fl
import tools.db_api as db
from tools.auth import AuthApi
import logging as log
from random import choice
from datetime import datetime, timedelta, timezone
import hashlib as hasher
import imghdr
from os import mkdir
from os.path import exists


bp = fl.Blueprint("bp_car_edit", __name__)


def pretty_num(price):
    return f"{price:_}".replace("_", " ")


def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")


@bp.route("/delete_car/<car_id>")
def delete_car(car_id):
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
        return res
    
    try:
        conn = db.DBConnection()
        user_role = conn.get_user_perms(user['message']['id'])
        if user_role['Allow_car_edit'] == False:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
        if user_role['Allow_car_add'] == False and car_id == None:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
    except Exception as e:
        log.error(e)
        fl.abort(500)
    finally:
        conn.close()
        
    try:
        conn = db.DBConnection()
        conn.executeonce("""
                         DELETE FROM public."Trade_car_imgs" WHERE car_id = %(car_id)s;
                         DELETE FROM public."Trade_cars" WHERE id = %(car_id)s;
                         """, {"car_id": car_id})
    except Exception as e:
        log.error(e)
        return fl.render_template("500.html")
    finally:
        conn.close()

    return fl.redirect(f"/sale")
        


@bp.route("/add_car", methods=["POST"])
def add_car():    
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
        return res
    
    try:
        conn = db.DBConnection()
        user_role = conn.get_user_perms(user['message']['id'])
        if user_role['Allow_car_edit'] == False:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
        if user_role['Allow_car_add'] == False and car_id == None:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
    except Exception as e:
        log.error(e)
        fl.abort(500)
    finally:
        conn.close()
    

    try:
        if fl.request.form.get("car_id") != "":
            car_id = int(fl.request.form.get("car_id"))
        else:
            car_id = None

        ### Проверка изображений
        files = dict(fl.request.files.lists())["files[]"]
        imgs = []
        allowed = [".jpg", ".jpeg", ".png"]
        for i in files:
            i.filename = hasher.md5(i.filename.encode()).hexdigest()
            valid = validate_image(i.stream)
            if valid in allowed:
                i.filename += valid
                imgs.append(i)

        if len(imgs) == 0 and car_id == None:
            res = fl.make_response(
                {
                    "status": False,
                    "message": "Необходимо загрузить хотя бы одно изображение",
                }
            )
            return res

        ### Проверка остальных полей
        input = fl.request.form.to_dict()
        del input["car_id"]
        specs = {}
        ints = [
            "year",
            "price",
            "hp",
            "mileage",
            "tank_capacity",
            "lenght",
            "width",
            "weight",
        ]
        selects = ["transmission", "body_type", "drive", "fuel_system", "fuel_type"]
        allowed_fields = [
            "brand",
            "model",
            "color",
            "year",
            "transmission",
            "vin",
            "hp",
            "drive",
            "fuel_type",
            "body_type",
            "mileage",
            "tank_capacity",
            "lenght",
            "width",
            "weight",
            "engine_capacity",
            "rating",
            "fuel_system",
            "price",
        ]

        if len(input) != 20:
            res = fl.make_response(
                {"status": False, "message": "Введите корректные данные"}
            )
            return res

        for i in input.items():
            if i[0] in ints:
                if i[1].isdigit():
                    specs[i[0]] = int(i[1])
                else:
                    res = fl.make_response(
                        {"status": False, "message": "Введите корректные данные"}
                    )
                    return res

            elif i[0] == "addto":
                
                if i[1] == "trade":
                    addto = "trade"
                elif i[1] == "auc":
                    addto = "auc"
                else:
                    res = fl.make_response({"status": False, "message": "Ты че, мышь"})
                    return res

            elif i[0] == "close_time":
                if i[1] != "":
                    try:
                        specs[i[0]] = datetime.strptime(i[1], "%Y-%m-%dT%H:%M")
                    except Exception as e:
                        log.error(e)
                        res = fl.make_response(
                            {"status": False, "message": "Введите корректные данные"}
                        )
                        return res

            elif i[0] == "rating":
                if len(i[1]) != 0:
                    specs[i[0]] = i[1][0].upper()
                else:
                    res = fl.make_response(
                        {"status": False, "message": "Введите корректные данные"}
                    )
                    return res

            elif i[0] in selects:
                if i[1].isdigit():
                    specs[i[0]] = int(i[1])
                elif i[1] == "":
                    res = fl.make_response(
                        {"status": False, "message": "Введите корректные данные"}
                    )
                    return res
                else:
                    res = fl.make_response({"status": False, "message": "Ты че, мышь"})
                    return res

            elif i[0] in allowed_fields:
                specs[i[0]] = i[1]

        conn = db.DBConnection()
        if addto == "trade":
            if car_id == None:
                add_res = conn.add_trade_car(**specs)
                carid = int(add_res["message"])
                mkdir(f"static/cars_imgs/{addto}_cars/{carid}")
                for i in imgs:
                    i.save(f"static/cars_imgs/{addto}_cars/{carid}/{i.filename}")
                conn.add_pics_2_trade_car([i.filename for i in imgs], carid)
            else:
                specs["car_id"] = car_id
                conn.executeonce(
                    """UPDATE public."Trade_cars" SET 
                            brand = %(brand)s, model = %(model)s,
                            color = %(color)s, year = %(year)s, transmission = %(transmission)s,
                            vin = %(vin)s, hp = %(hp)s, drive = %(drive)s,
                            fuel_type = %(fuel_type)s, body_type = %(body_type)s, mileage = %(mileage)s,
                            tank_capacity = %(tank_capacity)s, lenght = %(lenght)s, width = %(width)s,
                            weight = %(weight)s, rating = %(rating)s,
                            fuel_system = %(fuel_system)s, price = %(price)s WHERE id = %(car_id)s""", specs,
                )
                if not exists(f"static/cars_imgs/{addto}_cars/{car_id}"):
                    mkdir(f"static/cars_imgs/{addto}_cars/{car_id}")
                for i in imgs:
                    i.save(f"static/cars_imgs/{addto}_cars/{car_id}/{i.filename}")
                conn.add_pics_2_trade_car([i.filename for i in imgs], car_id)
                
        elif addto == "auc":
            log.error(specs)
            if car_id == None:
                add_res = conn.add_auc_car(**specs)
                carid = int(add_res["message"])
                mkdir(f"static/cars_imgs/{addto}_cars/{carid}")
                for i in imgs:
                    i.save(f"static/cars_imgs/{addto}_cars/{carid}/{i.filename}")
                conn.add_pics_2_auc_car([i.filename for i in imgs], carid)
            else:
                specs["car_id"] = car_id
                conn.executeonce(
                    """UPDATE public."Auction_cars" SET 
                            brand = %(brand)s, model = %(model)s,
                            color = %(color)s, year = %(year)s, transmission = %(transmission)s,
                            vin = %(vin)s, hp = %(hp)s, drive = %(drive)s,
                            fuel_type = %(fuel_type)s, body_type = %(body_type)s, mileage = %(mileage)s,
                            tank_capacity = %(tank_capacity)s, lenght = %(lenght)s, width = %(width)s,
                            weight = %(weight)s, rating = %(rating)s,
                            fuel_system = %(fuel_system)s, start_price = %(price)s, close_time = %(close_time)s WHERE id = %(car_id)s""", specs,
                )
                if not exists(f"static/cars_imgs/{addto}_cars/{car_id}"):
                    mkdir(f"static/cars_imgs/{addto}_cars/{car_id}")
                for i in imgs:
                    i.save(f"static/cars_imgs/{addto}_cars/{car_id}/{i.filename}")
                conn.add_pics_2_auc_car([i.filename for i in imgs], car_id)

        # fl.abort(404)

    except Exception as e:
        log.error(e)
        fl.abort(500)
    finally:
        conn.close()

    res = fl.make_response({"status": True, "message": "Автомобиль успешно добавлен!"})
    return res


@bp.route("/edit_car")
@bp.route("/edit_car/<car_id>")
def edit_car(car_id=None):
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
        return res
    
            


    try:
        conn = db.DBConnection()
        user_role = conn.get_user_perms(user['message']['id'])
        if user_role['Allow_car_edit'] == False:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
        if user_role['Allow_car_add'] == False and car_id == None:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
        
        if car_id != None:
            if fl.request.args.get("addto") == "auc":
                car = conn.get_auc_car(id=int(car_id))
                if car == None:
                    return fl.render_template("404.html")
                car["close_time"] = datetime.strftime(
                    car["close_time"], "%Y-%m-%dT%H:%M"
                )
                car["price"] = car["start_price"]

                imgs = list(i["pic_name"] for i in conn.get_auc_car_pics(car_id=car_id))
                addto = "auc"
            else:
                car = conn.get_trade_car(id=int(car_id))
                imgs = list(
                    i["pic_name"] for i in conn.get_trade_car_pics(car_id=car_id)
                )
                addto = "trade"

        conn.executeonce('SELECT * FROM "Transmissions"')
        trans = conn.fetchall()
        conn.executeonce('SELECT * FROM "Body_types"')
        body_types = conn.fetchall()
        conn.executeonce('SELECT * FROM "Drives"')
        drives = conn.fetchall()
        conn.executeonce('SELECT * FROM "Fuel_systems"')
        fuel_systems = conn.fetchall()

        conn.executeonce('SELECT * FROM "Fuel_types"')
        fuel_types = [
            {
                "id": i["id"],
                "name": (
                    f"{i['name']} ({i['quality']})"
                    if i["quality"] != None
                    else f"{i['name']}"
                ),
            }
            for i in conn.fetchall()
        ]

        # conn.close()
    except Exception as e:
        log.error(e)
        return fl.render_template("500.html")
    finally:
        conn.close()

    if car_id != None:
        return fl.render_template(
            "edit_car.html",
            **car,
            imgs=imgs,
            trans=trans,
            body_types=body_types,
            drives=drives,
            fuel_systems=fuel_systems,
            fuel_types=fuel_types,
            addto=addto,
        )
    else:
        return fl.render_template(
            "edit_car.html",
            brand="New",
            trans=trans,
            body_types=body_types,
            drives=drives,
            fuel_systems=fuel_systems,
            fuel_types=fuel_types,
            id=None
        )
