from os import urandom
import bcrypt
import re

from flasgger import Swagger, swag_from
from .docs.swagger import template

from flask import (
    Flask, abort, redirect
)
from flask_restful import (
    Api, Resource, reqparse
)
from flask_cors import CORS

from flaskext.mysql import MySQL
import names

# Regular Expression
SET = r"([0-9a-fA-F]{1,2}:){5}[0-9a-fA-F]{1,2}"

# CSRF protection & API keys
app = Flask(__name__)
app.secret_key = urandom(24)
api = Api(app)

# Swagger
app.config['SWAGGER'] = {
    'title': 'Team2 DinosaurGame',
    'uiversion': 2,
    'doc_dir': './docs/'
}
app.config['SWAGGER']['openapi'] = '2.0'
swagger = Swagger(app, template=template)
CORS(app)

# session cookie management
app.config.update(
    session_cookie_secure=True,
    session_cookie_httponly=True,
    session_cookie_samesite=''
)

# mysql cfg
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = ''  # Database username
app.config['MYSQL_DATABASE_PASSWORD'] = ''  # Database password
app.config['MYSQL_DATABASE_DB'] = ''  # Database table name
app.config['MYSQL_DATABASE_HOST'] = ''  # Database hosts name
app.config['MYSQL_DATABASE_PORT'] = 1234  # Database port
mysql.init_app(app)

# Receive client's data


class ParseRankData(Resource):
    def post(self):
        try:
            data = reqparse.RequestParser()
            data.add_argument('uid', type=str)
            data.add_argument('data', type=int)
            args = data.parse_args()

            uid = args['uid']
            if re.search(SET, uid) != None:
                uid = uid.encode('utf-8')

            if "SELECT" in uid or "DELETE" in uid:
                raise Exception("NoneType")

            uid = bcrypt.hashpw(uid, bcrypt.gensalt()).decode('utf-8')
            parsed_data = args['data']

            connection = mysql.connect()
            cursor = connection.cursor()
            cmd = "INSERT INTO user_log VALUES(%s, %s, NOW());"

            cursor.execute(cmd, (uid, parsed_data))
            connection.commit()
            result = cursor.fetchall()

            if len(result) == 0:
                return {'Message': 'Successfully Generated.'}
            else:
                return {'Message': 'failed to generate data sets.'}

        except Exception:
            return {'error': 'Please Check Your Data sets again.'}


# client's data request
class RequestRankData(Resource):
    def post(self):
        try:
            result = []

            data = reqparse.RequestParser()
            data.add_argument('uid', type=str)
            args = data.parse_args()

            uid = args['uid']

            if re.search(SET, uid) != None or uid == "test":
                uid = uid.encode('utf-8')

                if "SELECT" in uid.decode('utf-8') or ";" in uid.decode('utf-8') or "=" in uid.decode('utf-8') or "or" in uid.decode('utf-8') or "and" in uid.decode('utf-8'):
                    abort(401, "Invalid Contents.")

                else:
                    conn = mysql.connect()
                    cursor = conn.cursor()

                    cmd = "SELECT DISTINCT uid FROM user_log;"
                    cursor.execute(cmd)

                    data = cursor.fetchall()
                    if len(data) == 0:
                        pass

                    else:
                        for x in data:
                            for i in x:
                                if bcrypt.checkpw(uid, i.encode('utf-8')):
                                    cmd = "SELECT data FROM user_log WHERE uid = %s;"
                                    cursor.execute(cmd, i)

                                    data = cursor.fetchone()
                                    result.append(data[0])

                    result.sort()
                    result.reverse()

                    if 0 < len(result) < 5:
                        return {'Message': result[0:len(result):1]}
                    elif len(result) == 0:
                        return {'Message': []}
                    else:
                        return {'Message': result[0: 5: 1]}

            else:
                raise Exception("NoneType")

        except Exception as e:
            if "401" in str(e):
                abort(401, "Invalid Contents.")
            elif "NoneType" in str(e):
                abort(422, "Please Check Your Data sets again.")
            else:
                return {"Message": e}


class UserRankData(Resource):
    def post(self):
        """
        This is using docstrings for specifications.
        ---
        tags:
            - Rank
        parameters:
          - in: body
            required: false
            schema:
                type: object
                properties:
                    uid: {}
        responses:
            200:
                schema:
                    type: object
                    properties:
                        Args:
                            type: array
                            items:
                                type: array
                                items:
                                    oneOf:
                                      - type: integer
                                      - type: string
                        Message:
                            type: boolean
                            default: false
                        Count:
                            type: integer
                            format: int64
        """
        try:
            result = []
            count = 0
            user_data = [0, " "]

            isMe = False
            whereAmI = 0

            data = reqparse.RequestParser()
            data.add_argument('uid', type=str)
            args = data.parse_args()

            uid = args['uid']

            conn = mysql.connect()
            cursor = conn.cursor()

            cmd = "SELECT DISTINCT uid FROM user_log;"
            cursor.execute(cmd)

            data = cursor.fetchall()

            if uid == None:
                for x in data:
                    for i in x:
                        cmd = "SELECT data, uid FROM user_log WHERE uid = %s;"
                        cursor.execute(cmd, i)

                        data = cursor.fetchone()
                        result.append(list(data))

                result.sort()
                result.reverse()

                result = list(result[0:5:1])

            else:
                if re.search(SET, uid) == None and uid != "test":
                    if len(data) == 0:
                        pass

                    else:
                        for x in data:
                            for i in x:
                                cmd = "SELECT data, uid FROM user_log WHERE uid = %s;"
                                cursor.execute(cmd, i)

                                data = cursor.fetchone()
                                result.append(list(data))

                        result.sort()
                        result.reverse()

                        result = list(result[0:5:1])

                else:
                    if re.search(SET, uid) != None or uid == "test":
                        uid = uid.encode('utf-8')

                    if "SELECT" in uid.decode('utf-8') or ";" in uid.decode('utf-8') or "=" in uid.decode('utf-8') or "or" in uid.decode('utf-8') or "and" in uid.decode('utf-8'):
                        abort(401, "Invalid Contents.")

                    else:
                        conn = mysql.connect()
                        cursor = conn.cursor()

                        cmd = "SELECT uid FROM user_log;"
                        cursor.execute(cmd)

                        data = cursor.fetchall()
                        if len(data) == 0:
                            pass

                        else:
                            for x in data:
                                for i in x:
                                    cmd = "SELECT data, uid FROM user_log WHERE uid = %s;"

                                    cursor.execute(cmd, i)
                                    data = cursor.fetchone()

                                    if bcrypt.checkpw(uid, i.encode('utf-8')):
                                        if count == 0:
                                            count += 1

                                            command = "SELECT MAX(data), uid FROM user_log WHERE uid = %s"
                                            cursor.execute(command, i)

                                            user_data = cursor.fetchone()
                                            result.append(list(user_data))

                                        else:
                                            pass

                                    else:
                                        result.append(list(data))

                            result.sort(key=lambda num: num[0], reverse=True)
                            result = list(result[0:5:1])

            for a in range(0, 5):
                if user_data[1] == result[a][1]:
                    isMe = True
                    whereAmI = a + 1
                    result[a][1] = "You"

                else:
                    result[a][1] = names.get_first_name()

                    for k in range(0, 4):
                        for j in range(k+1, 5):
                            if result[k][1] == result[j][1]:
                                result[k][1] = names.get_last_name()

            if isMe:
                return {"Args": result, "Message": isMe, "Count": whereAmI}
            else:
                return {"Args": result, "Message": False, "Count": None}

        except Exception as e:
            abort(422, e)


# error handler
@ app.errorhandler(404)
def error404(error):
    return redirect("http://ec2-54-180-119-201.ap-northeast-2.compute.amazonaws.com/apidocs/")


@ app.errorhandler(500)
def error500(error):
    return redirect("http://ec2-54-180-119-201.ap-northeast-2.compute.amazonaws.com/apidocs/")


api.add_resource(ParseRankData, '/user/v1/data')
api.add_resource(RequestRankData, '/user/v1/info')
api.add_resource(UserRankData, '/user/v1/rank')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
