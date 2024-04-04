import flask as fl
import tools.db_api as db
import logging as log

bp = fl.Blueprint('bp_file1',__name__)
@bp.route('/')
def home():
    return fl.render_template('home.html', name="world1")


@bp.route('/test', methods=['GET','POST'])
def test():
    conn = db.DBConnection()
    methods = list(filter(lambda x: not x.startswith('_'), dir(conn)))
    if fl.request.method == 'POST':
        select = fl.request.form.get('test_select')
        args = fl.request.form.get('args')
        log.info(f"conn.{select}({args})")
        name = eval(f"conn.{select}({args})")
        # name = select
    else:
        # conn.add_auc_car(body_type="Седан")
        name = "world"
    return fl.render_template('home.html', name=name, option=methods)

@bp.route('/test_button')
def test_button():
    return fl.redirect('/test')