import psycopg2
import psycopg2.extras 
from psycopg2.extensions import AsIs
import json
import logging as log

class AucActions:
    HIDE = "Hide"
    UNHIDE = "Unhide"
    SOLD = "Sold"
    BET = "Bet"

class DBConnection:
    def __init__(self):
        try:
            f = open("tools/db_creds.json")
            db_creds = json.load(f)

            self.conn = psycopg2.connect(
                dbname=db_creds["dbname"],
                host=db_creds["host"],
                user=db_creds["user"],
                password=db_creds["password"],
                port=db_creds["port"],
            )
            # conn.autocommit = True
            self.cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            f.close()
        except Exception as Exc:
            log.error(Exc)

    def close(self):
        self.conn.close()

    def executeonce(self, promt: str, params = [], dictCur: bool = False):
        try:
            self.cur.execute(promt, params)
            self.conn.commit()
        except Exception as Exc:
            log.error(Exc)

    def execute(self, promt: str, params = []):
        self.cur.execute(promt, params)

    def commit(self):
        return self.conn.commit()

    def fetchall(self):
        return self.cur.fetchall()
    
    def fetchone(self):
        return self.cur.fetchone()


    def add_auc_car(
            self, brand = None, model = None,
            color = None, year = None, transmission = None,
            vin = None, hp = None, drive = None,
            fuel_type = None, body_type = None, mileage = None,
            tank_capacity = None, lenght = None, width = None,
            weight = None, engine_capacity = None, rating = None,
            fuel_system = None, start_price = 0, close_time = None) -> dict:
        try:
            if type(body_type) != int and body_type != None:
                self.executeonce("SELECT id FROM public.\"Body_types\" WHERE name = %(body_type)s", {"body_type": body_type})
                body_type = self.fetchone["id"]
            if type(drive) != int and drive != None:
                self.executeonce("SELECT id FROM public.\"Drives\" WHERE name = %(drive)s", {"drive": drive})
                drive = self.fetchone["id"]
            if type(fuel_system) != int and fuel_system != None:
                self.executeonce("SELECT id FROM public.\"Fuel_systems\" WHERE name = %(fuel_system)s", {"fuel_system": fuel_system})
                fuel_system = self.fetchone["id"]
            if type(fuel_type) != int and fuel_type != None:
                self.executeonce("SELECT id FROM public.\"Fuel_types\" WHERE name = %(fuel_type)s", {"fuel_type": fuel_type})
                fuel_type = self.fetchone["id"]
            if type(transmission) != int and transmission != None:
                self.executeonce("SELECT id FROM public.\"Transmissions\" WHERE name = %(transmission)s", {"transmission": transmission})
                transmission = self.fetchone["id"]
                
            prompt = 'INSERT INTO public."Auction_cars"(brand, model, color, year, transmission, vin, hp, drive, fuel_type, body_type, mileage, tank_capacity, lenght, width, weight, engine_capacity, rating, fuel_system, start_price, close_time)\
                VALUES (%(brand)s, %(model)s, %(color)s, %(year)s, %(transmission)s, %(vin)s, %(hp)s, %(drive)s, %(fuel_type)s, %(body_type)s, %(mileage)s, %(tank_capacity)s, %(lenght)s, %(width)s, %(weight)s, %(engine_capacity)s, %(rating)s, %(fuel_system)s, %(start_price)s, %(close_time)s) RETURNING id;'
            self.executeonce( prompt, {"brand": brand, "model": model, "color": color,
                                        "year": year, "transmission": transmission, "vin": vin,
                                        "hp": hp, "drive": drive, "fuel_type": fuel_type,
                                        "body_type": body_type, "mileage": mileage, "tank_capacity": tank_capacity,
                                        "lenght": lenght, "width": width, "weight": weight,
                                        "engine_capacity": engine_capacity, "rating": rating, "fuel_system": fuel_system,
                                        "start_price": start_price, "close_time": close_time})
            
            return {"status": True, "message": f"{self.fetchone()['id']}"}
        except Exception as e:
            log.error(e)
            return {"status": False, "message": f"{e}"}

    def add_trade_car(
            self, brand = None, model = None,
            color = None, year = None, transmission = None,
            vin = None, hp = None, drive = None,
            fuel_type = None, body_type = None, mileage = None,
            tank_capacity = None, lenght = None, width = None,
            weight = None, engine_capacity = None, rating = None,
            fuel_system = None, price = 0, status = 1) -> dict:

        try:
            if type(body_type) != int and body_type != None:
                self.executeonce("SELECT id FROM public.\"Body_types\" WHERE name = %(body_type)s", {"body_type": body_type})
                body_type = self.fetchone["id"]
            if type(drive) != int and drive != None:
                self.executeonce("SELECT id FROM public.\"Drives\" WHERE name = %(drive)s", {"drive": drive})
                drive = self.fetchone["id"]
            if type(fuel_system) != int and fuel_system != None:
                self.executeonce("SELECT id FROM public.\"Fuel_systems\" WHERE name = %(fuel_system)s", {"fuel_system": fuel_system})
                fuel_system = self.fetchone["id"]
            if type(fuel_type) != int and fuel_type != None:
                self.executeonce("SELECT id FROM public.\"Fuel_types\" WHERE name = %(fuel_type)s", {"fuel_type": fuel_type})
                fuel_type = self.fetchone["id"]
            if type(transmission) != int and transmission != None:
                self.executeonce("SELECT id FROM public.\"Transmissions\" WHERE name = %(transmission)s", {"transmission": transmission})
                transmission = self.fetchone["id"]
            if type(status) != int and status != None:
                self.executeonce("SELECT id FROM public.\"States\" WHERE name = %(status)s", {"status": status})
                status = self.fetchone["id"]
                
            prompt = 'INSERT INTO public."Trade_cars"(brand, model, color, year, transmission, vin, hp, drive, fuel_type, body_type, mileage, tank_capacity, lenght, width, weight, engine_capacity, rating, fuel_system, price, status)\
                        VALUES (%(brand)s, %(model)s, %(color)s, %(year)s, %(transmission)s, %(vin)s, %(hp)s, %(drive)s, %(fuel_type)s, %(body_type)s, %(mileage)s, %(tank_capacity)s, %(lenght)s, %(width)s, %(weight)s, %(engine_capacity)s, %(rating)s, %(fuel_system)s, %(price)s, %(status)s) RETURNING id;'
            self.executeonce( prompt, {"brand": brand, "model": model, "color": color,
                                        "year": year, "transmission": transmission, "vin": vin,
                                        "hp": hp, "drive": drive, "fuel_type": fuel_type,
                                        "body_type": body_type, "mileage": mileage, "tank_capacity": tank_capacity,
                                        "lenght": lenght, "width": width, "weight": weight,
                                        "engine_capacity": engine_capacity, "rating": rating, "fuel_system": fuel_system,
                                        "price": price, "status": status})

            return {"status": True, "message": f"{self.fetchone()['id']}"}
            
        except Exception as e:
            log.error(e)
            return {"status": False, "message": f"{e}"}
        
    def add_pics_2_auc_car(self, pics: list, car_id: int) -> dict: 
        try:
            for pic in pics:
                self.executeonce("INSERT INTO public.\"Auction_car_imgs\"(pic_name, car_id)\
                                    VALUES (%(pic_name)s, %(car_id)s);", {"pic_name": pic, "car_id": car_id})
            return {"status": True, "message": "Successfully added new pics"}
        except Exception as e:
            log.error(e)
            return {"status": False, "message": f"{e}"}
                
    def add_pics_2_trade_car(self, pics: list, car_id: int) -> dict: 
        try:
            for pic in pics:
                self.executeonce("INSERT INTO public.\"Trade_car_imgs\"(pic_name, car_id)\
                                    VALUES (%(pic_name)s, %(car_id)s);", {"pic_name": pic, "car_id": car_id})
            return {"status": True, "message": "Successfully added new pics"}
        except Exception as e:
            log.error(e)
            return {"status": False, "message": f"{e}"}
                



    def add_user(self, name, surname, 
                 phone_number, birthday, passkey,
                 email, role = "User") -> dict:
        try:
            self.executeonce("""SELECT (SELECT COUNT(*) FROM "Users" 
                             WHERE "Email" = %(email)s) = 0 as check""", 
                             {"email":email})
            if self.fetchone()["check"] == 0:
                return {"status": False, "message": "Пользователь с такой почтой или телефоном уже зарегистрирован"}
                                                
            if type(role) != int:
                self.executeonce("SELECT id FROM public.\"Roles\" WHERE \"Name\" = %(role)s", {"role": role})
                role = self.fetchone()["id"]
            
            prompt = 'INSERT INTO public."Users"("Name", "Surname", "Phone_number", "Email", "Birthday", "Passkey", "Role_id")\
                        VALUES (%(name)s, %(surname)s, %(phone_number)s, %(email)s, %(birthday)s, %(passkey)s, %(role)s);'
            
            self.executeonce( prompt, {"name":name, "surname":surname, 
                                        "phone_number":phone_number, "birthday":birthday, "passkey":passkey,
                                        "email":email, "role":role})

            return {"status": True, "message": "Пользователь добавлен"}
            
        except Exception as e:
            log.error(e)
            return {"status": False, "message": f"{e}"}
        
        
    def insert_to_auc_history(self, user_id: int, car_id: int, action: str, action_info: str):
        """
        Actions:
            - Bet
            - Hide
            - Unhide
            - Sold
        """
        try:
            if action not in ["Bet", "Hide", "Unhide", "Sold"]:
                raise ValueError(f"Invalid action ({action})")
            
            if self.get_auc_car_status(car_id) == "Sold":
                raise ValueError("Car is already sold")
            
            prompt = 'INSERT INTO public."Auction_history" (user_id, car_id, action, action_info) \
	                    VALUES (%(user_id)s, %(car_id)s, %(action)s, %(action_info)s);'
            
            self.executeonce( prompt, {"user_id":user_id, "car_id":car_id, "action":action, "action_info":action_info})
            return True
        
        except Exception as e:
            log.error(e)
            return False
     
    def set_auc_car_status(self, user_id: int, car_id: int, status: AucActions, comment: str = ""):
        self.insert_to_auc_history(user_id, car_id, status, action_info=comment)
        
    def get_auc_car_price(self, car_id):
        try:
            self.executeonce("""SELECT SUM(CAST("action_info" AS INT)) FROM "Auction_history"
                             WHERE "action" = 'Bet' AND "car_id" = %(car_id)s""", {"car_id": car_id})
            return self.cur.fetchone()['sum']
        
        except Exception as e:
            log.error(e)
    
    def get_auc_car_current_price(self, car_id):
        try:
            self.executeonce("""SELECT start_price FROM "Auction_cars"
                             WHERE id = %(car_id)s""", {"car_id": car_id})
            
            price = int(self.cur.fetchone()["start_price"])
            
            self.executeonce("""SELECT SUM(CAST("action_info" AS INT)) FROM "Auction_history"
                             WHERE "action" = 'Bet' AND "car_id" = %(car_id)s""", {"car_id": car_id})
            
            curr_price = self.cur.fetchone()['sum']
            price += int(curr_price) if curr_price != None else 0
            return price
        
        except Exception as e:
            log.error(e)
        
    def get_auc_car_status(self, car_id):
        try:
            self.executeonce("""SELECT "action" FROM "Auction_history"
                             WHERE "action" != 'Bet' AND "car_id" = %(car_id)s 
                             ORDER BY timestamp DESC LIMIT 1""", {"car_id": car_id})
            return self.cur.fetchone()['action']
        
        except Exception as e:
            log.error(e)


    def get_auc_car(self, id = None, limit = None, closed = False, where = True):
        try:
            if id != None:
                self.executeonce("""SELECT "Auction_cars".id, "Auction_cars".brand, "Auction_cars".model, "Auction_cars".color,
                                        "Auction_cars".year, "Auction_cars".vin, "Auction_cars".hp, "Auction_cars".mileage, "Auction_cars".tank_capacity,
                                        "Auction_cars".lenght, "Auction_cars".width, "Auction_cars".weight, "Auction_cars".engine_capacity, 
                                        "Auction_cars".rating, "Auction_cars".start_price, "Auction_cars".close_time,
                                        "Transmissions".name as transmission, "Drives".name as drive, "Fuel_types".name as fuel_type, "Fuel_types".quality as fuel_qual,
                                        "Body_types".name as body_type, "Fuel_systems".name as fuel_system
                                        FROM PUBLIC."Auction_cars"
                                        JOIN "Transmissions" ON "Auction_cars".transmission = "Transmissions".id
                                        JOIN "Drives" ON "Auction_cars".drive = "Drives".id
                                        JOIN "Fuel_types" ON "Auction_cars".fuel_type = "Fuel_types".id
                                        JOIN "Body_types" ON "Auction_cars".body_type = "Body_types".id
                                        JOIN "Fuel_systems" ON "Auction_cars".fuel_system = "Fuel_systems".id
                                        WHERE "Auction_cars".id = %(id)s
                                """, {"id": id})
                return dict(self.cur.fetchone())
            elif closed == False:
                self.executeonce(f"""SELECT "Auction_cars".id, "Auction_cars".brand, "Auction_cars".model, "Auction_cars".color,
                                        "Auction_cars".year, "Auction_cars".vin, "Auction_cars".hp, "Auction_cars".mileage, "Auction_cars".tank_capacity,
                                        "Auction_cars".lenght, "Auction_cars".width, "Auction_cars".weight, "Auction_cars".engine_capacity, 
                                        "Auction_cars".rating, "Auction_cars".start_price, "Auction_cars".close_time,
                                        "Transmissions".name as transmission, "Drives".name as drive, "Fuel_types".name as fuel_type, "Fuel_types".quality as fuel_qual,
                                        "Body_types".name as body_type, "Fuel_systems".name as fuel_system
                                        FROM PUBLIC."Auction_cars"
                                        JOIN "Transmissions" ON "Auction_cars".transmission = "Transmissions".id
                                        JOIN "Drives" ON "Auction_cars".drive = "Drives".id
                                        JOIN "Fuel_types" ON "Auction_cars".fuel_type = "Fuel_types".id
                                        JOIN "Body_types" ON "Auction_cars".body_type = "Body_types".id
                                        JOIN "Fuel_systems" ON "Auction_cars".fuel_system = "Fuel_systems".id
                                        WHERE ((SELECT "action" FROM "Auction_history" WHERE "car_id" = "Auction_cars".id ORDER BY timestamp DESC LIMIT 1) != 'Sold'
                                                OR (SELECT count("action") FROM (SELECT "action" FROM "Auction_history" WHERE "car_id" = "Auction_cars".id ORDER BY timestamp DESC LIMIT 1)) = 0)
                                        AND close_time > CURRENT_TIMESTAMP
                                        AND {where} ORDER BY close_time ASC LIMIT %(limit)s""", {"limit": limit})
                return list(map(dict, self.cur.fetchall()))
            else:
                self.executeonce(f"""SELECT "Auction_cars".id, "Auction_cars".brand, "Auction_cars".model, "Auction_cars".color,
                                        "Auction_cars".year, "Auction_cars".vin, "Auction_cars".hp, "Auction_cars".mileage, "Auction_cars".tank_capacity,
                                        "Auction_cars".lenght, "Auction_cars".width, "Auction_cars".weight, "Auction_cars".engine_capacity, 
                                        "Auction_cars".rating, "Auction_cars".start_price, "Auction_cars".close_time,
                                        "Transmissions".name as transmission, "Drives".name as drive, "Fuel_types".name as fuel_type, "Fuel_types".quality as fuel_qual,
                                        "Body_types".name as body_type, "Fuel_systems".name as fuel_system
                                        FROM PUBLIC."Auction_cars"
                                        JOIN "Transmissions" ON "Auction_cars".transmission = "Transmissions".id
                                        JOIN "Drives" ON "Auction_cars".drive = "Drives".id
                                        JOIN "Fuel_types" ON "Auction_cars".fuel_type = "Fuel_types".id
                                        JOIN "Body_types" ON "Auction_cars".body_type = "Body_types".id
                                        JOIN "Fuel_systems" ON "Auction_cars".fuel_system = "Fuel_systems".id
                                        WHERE {where} LIMIT %(limit)s""", {"limit": limit})
                return list(map(dict, self.cur.fetchall()))
        
        except Exception as e:
            log.error(e)
        
    def get_trade_car(self, id = None, limit=None, sortby="id", all=False):
        try:
            if id != None:
                self.executeonce("""SELECT "Trade_cars".id, "Trade_cars".brand, "Trade_cars".model, "Trade_cars".color,
                                        "Trade_cars".year, "Trade_cars".vin, "Trade_cars".hp, "Trade_cars".mileage, "Trade_cars".tank_capacity,
                                        "Trade_cars".lenght, "Trade_cars".width, "Trade_cars".weight, "Trade_cars".engine_capacity, 
                                        "Trade_cars".rating, "Trade_cars".price,
                                        "Transmissions".name as transmission, "Drives".name as drive, "Fuel_types".name as fuel_type, "Fuel_types".quality as fuel_qual,
                                        "Body_types".name as body_type, "Fuel_systems".name as fuel_system, "States".title as status
                                        FROM PUBLIC."Trade_cars"
                                        JOIN "Transmissions" ON "Trade_cars".transmission = "Transmissions".id
                                        JOIN "Drives" ON "Trade_cars".drive = "Drives".id
                                        JOIN "Fuel_types" ON "Trade_cars".fuel_type = "Fuel_types".id
                                        JOIN "Body_types" ON "Trade_cars".body_type = "Body_types".id
                                        JOIN "Fuel_systems" ON "Trade_cars".fuel_system = "Fuel_systems".id
                                        JOIN "States" ON "Trade_cars".status = "States".id
                                        WHERE "Trade_cars".id = %(id)s
                                """, {"id": id})
                return dict(self.cur.fetchone())
            elif (all == False):
                self.executeonce("""SELECT "Trade_cars".id, "Trade_cars".brand, "Trade_cars".model, "Trade_cars".color,
                        "Trade_cars".year, "Trade_cars".vin, "Trade_cars".hp, "Trade_cars".mileage, "Trade_cars".tank_capacity,
                        "Trade_cars".lenght, "Trade_cars".width, "Trade_cars".weight, "Trade_cars".engine_capacity, 
                        "Trade_cars".rating, "Trade_cars".price,
                        "Transmissions".name as transmission, "Drives".name as drive, "Fuel_types".name as fuel_type, "Fuel_types".quality as fuel_qual,
                        "Body_types".name as body_type, "Fuel_systems".name as fuel_system, "States".title as status
                        FROM PUBLIC."Trade_cars"
                        JOIN "Transmissions" ON "Trade_cars".transmission = "Transmissions".id
                        JOIN "Drives" ON "Trade_cars".drive = "Drives".id
                        JOIN "Fuel_types" ON "Trade_cars".fuel_type = "Fuel_types".id
                        JOIN "Body_types" ON "Trade_cars".body_type = "Body_types".id
                        JOIN "Fuel_systems" ON "Trade_cars".fuel_system = "Fuel_systems".id
                        JOIN "States" ON "Trade_cars".status = "States".id
                        WHERE "Trade_cars".status = 1 ORDER BY %(sortby)s LIMIT %(limit)s""",
                        {"sortby": AsIs(sortby), "limit": limit})
                return list(map(dict, self.cur.fetchall()))
            else:
                self.executeonce("""SELECT "Trade_cars".id, "Trade_cars".brand, "Trade_cars".model, "Trade_cars".color,
                        "Trade_cars".year, "Trade_cars".vin, "Trade_cars".hp, "Trade_cars".mileage, "Trade_cars".tank_capacity,
                        "Trade_cars".lenght, "Trade_cars".width, "Trade_cars".weight, "Trade_cars".engine_capacity, 
                        "Trade_cars".rating, "Trade_cars".price,
                        "Transmissions".name as transmission, "Drives".name as drive, "Fuel_types".name as fuel_type, "Fuel_types".quality as fuel_qual,
                        "Body_types".name as body_type, "Fuel_systems".name as fuel_system, "States".title as status
                        FROM PUBLIC."Trade_cars"
                        JOIN "Transmissions" ON "Trade_cars".transmission = "Transmissions".id
                        JOIN "Drives" ON "Trade_cars".drive = "Drives".id
                        JOIN "Fuel_types" ON "Trade_cars".fuel_type = "Fuel_types".id
                        JOIN "Body_types" ON "Trade_cars".body_type = "Body_types".id
                        JOIN "Fuel_systems" ON "Trade_cars".fuel_system = "Fuel_systems".id
                        JOIN "States" ON "Trade_cars".status = "States".id
                        ORDER BY %(sortby)s LIMIT %(limit)s""",
                        {"sortby": AsIs(sortby), "limit": limit})
                return list(map(dict, self.cur.fetchall()))
        
        except Exception as e:
            log.error(e)
    
    def get_auc_car_pics(self, car_id: int) -> list:
        try:
            self.executeonce("SELECT pic_name FROM public.\"Auction_car_imgs\"\
                    WHERE car_id = %(car_id)s;", {"car_id": car_id})
            return list(map(dict, self.cur.fetchall()))
        except Exception as e:
            log.error(e)
            return {"status": False, "message": f"{e}"}
    
    def get_trade_car_pics(self, car_id: int) -> list:
        try:
            self.executeonce('SELECT pic_name FROM public."Trade_car_imgs" WHERE car_id = %(car_id)s;', {"car_id": car_id})
            return list(map(dict, self.cur.fetchall()))
        except Exception as e:
            log.error(e)
            return {"status": False, "message": f"{e}"}
    
    def get_user_perms(self, user_id):
        try:
            self.executeonce("""SELECT "Users"."id", "Roles"."Name" as role, "Roles"."Allow_car_add", "Roles"."Allow_car_edit", 
                                    "Roles"."Allow_ext_car_view", "Roles"."Allow_manage_users"
                                    FROM "Roles" JOIN "Users" ON "Roles".id = "Users"."Role_id" WHERE "Users".id = %(id)s
                             """, {"id": user_id})
            return dict(self.cur.fetchone())
        
        except Exception as e:
            log.error(e)

    def get_user_by_id(self, user_id):
        try:
            self.executeonce("""SELECT id, "Name", "Surname", "Phone_number", "Email", "Birthday", "Passkey" 
                             FROM public."Users" WHERE id = %(id)s""", {"id": user_id})
            return dict(self.cur.fetchone())
        
        except Exception as e:
            log.error(e)
    
    def get_user(self, email, passkey):  
        try:      
            self.executeonce("WITH cte AS (SELECT * FROM \"Users\" WHERE \"Email\" = %(email)s AND \"Passkey\" = %(passkey)s) SELECT * FROM cte FULL JOIN (SELECT EXISTS(SELECT * FROM cte)) ON true;", {"email": email, "passkey": passkey})
            res = self.fetchone()
            return dict(res)
        except Exception as e:
            log.error(e)
            return False