from flask import Flask
from flask import render_template
import ssl
import logging
import logging.handlers
from datetime import date

### Import BPs
import index
import auction.index as aucindex
import tools.auth as auth
import trade.sale as sale
import trade.car_details as cdet
import admin.edit_car as cedit
###

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert/certificate.crt', 'cert/private.key')

app = Flask(__name__)
app.register_blueprint(index.bp)
app.register_blueprint(aucindex.bp)
app.register_blueprint(auth.bp)
app.register_blueprint(sale.bp)
app.register_blueprint(cdet.bp)
app.register_blueprint(cedit.bp)


app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

@app.route('/.well-known/pki-validation/1FCC9AFF590712C8FF1FAF551AEC12FB.txt')
def cert():
  return open("cert.txt").read()

@app.errorhandler(404)
def error404(e):
  return render_template('404.html'), 404

@app.errorhandler(500)
def error500(e):
  return render_template('500.html'), 500

@app.errorhandler(403)
def error403(e):
  return render_template('403.html'), 403
   

if __name__ == '__main__':
  file_logger = logging.getLogger("")
  file_logger.setLevel(logging.DEBUG)
  fl_handler = logging.handlers.RotatingFileHandler(filename=f"logs/{date.today().strftime('%Y-%m-%d')}.log",
                                                    maxBytes=1500000, backupCount=24, mode='a', encoding='utf-8')
  fl_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
  file_logger.addHandler(fl_handler)
  
  app.run(host="82.97.242.148", port=443, debug=True, ssl_context=context)