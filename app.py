from flask import Flask
from flask import render_template
import index
import ssl
import logging
import logging.handlers
from datetime import date

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert/certificate.crt', 'cert/private.key')

app = Flask(__name__)
app.register_blueprint(index.bp)


@app.route('/.well-known/pki-validation/1FCC9AFF590712C8FF1FAF551AEC12FB.txt')
def cert():
  return open("cert.txt").read()

if __name__ == '__main__':
  file_logger = logging.getLogger("")
  file_logger.setLevel(logging.DEBUG)
  fl_handler = logging.handlers.RotatingFileHandler(filename=f"logs/{date.today().strftime('%Y-%m-%d')}.log",
                                                    maxBytes=5000000, backupCount=24, mode='a', encoding='utf-8')
  fl_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
  file_logger.addHandler(fl_handler)
  
  app.run(host="82.97.242.148", port=443, debug=True, ssl_context=context)