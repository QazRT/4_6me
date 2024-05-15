from flask import Flask
from flask import render_template
from flask_mail import Mail
import ssl
import logging
import logging.handlers
from datetime import date
from apscheduler.schedulers.background import BackgroundScheduler
import tools.db_api as db

### Import BPs
import index
import auction.index as aucindex
import tools.auth as auth
import trade.sale as sale
import trade.car_details as cdet
import admin.edit_car as cedit
import admin.view_all_auc_cars as adminauc

###

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain("cert/certificate.crt", "cert/private.key")

app = Flask(__name__)
app.register_blueprint(index.bp)
app.register_blueprint(aucindex.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(sale.bp)
app.register_blueprint(cdet.bp)
app.register_blueprint(cedit.bp)
app.register_blueprint(adminauc.bp)


app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024
app.config["MAIL_SERVER"] = "smtp.nobless-oblige.ru"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["MAIL_USERNAME"] = "noreply@nobless-oblige.ru"
app.config["MAIL_DEFAULT_SENDER"] = "noreply@nobless-oblige.ru"
app.config["MAIL_PASSWORD"] = "password"

mail = Mail(app)


@app.route("/.well-known/pki-validation/1FCC9AFF590712C8FF1FAF551AEC12FB.txt")
def cert():
    return open("cert.txt").read()


@app.errorhandler(404)
def error404(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def error500(e):
    return render_template("500.html"), 500


@app.errorhandler(403)
def error403(e):
    return render_template("403.html"), 403


def check_aucs():
    try:
        conn = db.DBConnection()
        conn.executeonce(
            """SELECT id FROM "Auction_cars" WHERE close_time <= CURRENT_TIMESTAMP"""
        )
        ids = [ row['id'] for row in conn.fetchall() ]
        for id in ids:
            conn.executeonce("""SELECT user_id FROM "Auction_history" WHERE car_id = %(id)s ORDER BY timestamp DESC LIMIT 1""", 
                                    {"id": id})
            userid = conn.fetchone()['user_id']
            conn.set_auc_car_status(car_id=id, user_id=userid, status=db.AucActions.SOLD)

    except Exception as e:
        logging.error(e)
    finally:
        conn.close()


sched = BackgroundScheduler(daemon=True)
sched.add_job(check_aucs, "cron", minute=0)
sched.start()

if __name__ == "__main__":
    file_logger = logging.getLogger("")
    file_logger.setLevel(logging.DEBUG)
    fl_handler = logging.handlers.RotatingFileHandler(
        filename=f"logs/{date.today().strftime('%Y-%m-%d')}.log",
        maxBytes=1500000,
        backupCount=24,
        mode="a",
        encoding="utf-8",
    )
    fl_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    file_logger.addHandler(fl_handler)
    
    check_aucs()
    
    app.run(host="82.97.242.148", port=443, debug=True, ssl_context=context)
