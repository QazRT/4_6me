import flask as fl
import tools.db_api as db
from tools.auth import AuthApi
import logging as log

bp = fl.Blueprint("bp_admin_users", __name__)


def pretty_phone(phone) -> str:
    if len(phone) != 11 or phone.isdigit() == False:
        return "8 (800) 555-35-35"
    
    return f"8 ({phone[1:4]}) {phone[4:7]}-{phone[7:9]}-{phone[9:11]}"

@bp.route("/update_user/<id>", methods=["POST"])
def update_user(id):
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        return fl.redirect(f"/?auth=1")
    try:
        conn = db.DBConnection()
        user_role = conn.get_user_perms(user["message"]["id"])
        if user_role["Allow_manage_users"] == False:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
        
        conn.executeonce("SELECT EXISTS (SELECT * FROM public.\"Users\" WHERE id = %(id)s) AS \"exists\"", {"id": id})
        res = dict(conn.fetchone())['exists']
        if res == False:
            return fl.render_template("404.html")
            # return "Hui"
        
        if fl.request.form.get("role_id") == None:
            return fl.make_response("", 400)
        
        conn.executeonce("""
                         UPDATE public."Users" SET "Role_id"  =  %(role_id)s WHERE id = %(id)s
                         """, {"role_id": fl.request.form.get("role_id"), "id": id})
        
    except Exception as e:
        log.error(e)
        fl.abort(500)
    finally:
        conn.close()

    res = fl.make_response({"status": True, "message": "Пользователь успешно обновлен!"})
    return res


@bp.route("/delete_user/<user_id>", methods=["POST"])
def delete_user(user_id):
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        return fl.redirect(f"/?auth=1")
    try:
        conn = db.DBConnection()
        user_role = conn.get_user_perms(user["message"]["id"])
        if user_role["Allow_manage_users"] == False:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
        
        conn.executeonce("SELECT EXISTS (SELECT * FROM public.\"Users\" WHERE id = %(id)s) AS \"exists\"", {"id": user_id})
        res = dict(conn.fetchone())['exists']
        if res == False:
            return fl.render_template("404.html")
                
        conn.executeonce("""
                         DELETE FROM public."Users" WHERE id = %(id)s
                         """, {"id": fl.request.form.get("user_id")})
        
    except Exception as e:
        log.error(e)
        fl.abort(500)
    finally:
        conn.close()

    res = fl.make_response({"status": True, "message": "Пользователь успешно удален!"})
    return res

@bp.route("/users")
def view_users():
    user = AuthApi.is_loggged_in()
    if user["status"] == False:
        return fl.redirect(f"/?auth=1")
    try:
        conn = db.DBConnection()
        user_role = conn.get_user_perms(user["message"]["id"])
        if user_role["Allow_manage_users"] == False:
            res = fl.make_response(fl.redirect(f"/?auth=1"), 403)
            return res
        
        conn.executeonce("""
                                 SELECT "Users".id, "Users"."Name", "Surname", "Phone_number", "Email", "Role_id", 
                                            "Roles"."Name" as "Role_name"
                                            FROM public."Users" JOIN public."Roles" 
                                            ON "Users"."Role_id" = "Roles".id
                                 """)
        users = list(map(dict, conn.fetchall()))
        # log.warn(users)
        for u in users:
            u['Phone_number'] = pretty_phone(u['Phone_number'])
        
        conn.executeonce("""SELECT id, "Name" as "name" FROM public."Roles" WHERE id >= %(user_role_id)s""",
                                 {"user_role_id": user["message"]["Role_id"]})
        
        roles = list(map(dict, conn.fetchall()))
        
    except Exception as e:
        log.error(e)
        fl.abort(500)
    finally:
        conn.close()

    return fl.render_template("users.html", users=users, roles=roles)
