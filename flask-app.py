from recom import *
from flask import Flask
from flask_restx import Resource,Api

app=Flask(__name__)
api=Api(app,version='1.0',title='Recommendation API',description='API for Content Recommendation')
ns=api.namespace('custom',description='operations')
app.config.SWAGGER_UI_DOC_EXPANSION='full'

#@api.route('/<string:text>')
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

app.run(host='127.0.0.1',debug=True,port=5001)
