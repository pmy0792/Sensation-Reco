from recom import *
from flask import Flask
from flask_restx import Resource,Api
from flask_cors import CORS
from flask import url_for,redirect
app=Flask(__name__)
CORS(app)

api=Api(app,version='1.0',title='Recommendation API',description='API for Content Recommendation')
ns=api.namespace('custom',description='operations')
app.config.SWAGGER_UI_DOC_EXPANSION='full'
#app.add_url_rule('/favicon.ico',
                 #redirect_to=url_for("static",filename='favicon.ico'))

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static', filename='favicon.ico'))
@api.response(200,'Found')
@api.response(404,'Not found')
@api.response(500,'Internal Error')
#@api.param('text','String Value')

@api.route("/<string:user_id>")
class Algorithm(Resource):
    @api.doc('get')
    def get(self,user_id):
        user_id=int(user_id)
        rec = get_rec(user_id)

        return {"recommend-list":rec}


@app.route("/<string:user_id>")
def home():
    return "Home"

app.run(host='0.0.0.0',debug=True,port=5000)
#app.run(host='127.0.0.1',debug=True,port=5001)