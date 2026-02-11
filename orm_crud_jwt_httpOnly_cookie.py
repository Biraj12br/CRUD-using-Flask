from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt,
    set_access_cookies,
    set_refresh_cookies,
    unset_jwt_cookies)

from datetime import timedelta, datetime, timezone
#timezone.utc is essential for JWTs.

app = Flask(__name__)

# Database configuration
app.config['SECRET_KEY']='myapp351'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:Biraj351@localhost/flask'

#JWT Config
app.config['JWT_SECRET_KEY']='secret_key'
app.config['JWT_TOKEN_LOCATION']=['cookies']
app.config['JWT_ACCESS_COOKIE_NAME']='access_token'
app.config['JWT_REFRESH_COOKIE_NAME']='refresh_token'
app.config['JWT_COOKIE_CSRF_PROTECT']=False
app.config['JWT_COOKIE_SECURE']=False
app.config['JWT_COOKIE_SAMESITE']='Lax'

#Expiry
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(hours=1)

db = SQLAlchemy(app)

jwt=JWTManager(app)

#Table Creation
class User(db.Model):
    id = db.Column(db.Integer,autoincrement=True, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    #    __table_args__ = {'autoload_with': db.engine}  Use this if the db already exists.

    #Method for displaying data
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email
        }

#Blocklist Token Class
class TokenBlocklist(db.Model):

    id = db.Column(db.Integer, autoincrement=True, primary_key=True, )
    jti = db.Column(db.String(36), nullable=False, index=True)
    token_type = db.Column(db.String(10), nullable=False)  # access / refresh
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=False)


#POST(Tokens Generation)
@app.route('/login',methods=['POST'])
def login():
    username = request.json.get("username")

    access_token = create_access_token(identity=username)
    refresh_token = create_refresh_token(identity=username)

    response = jsonify(message="Login successful")
    set_access_cookies(response, access_token)
    set_refresh_cookies(response, refresh_token)

    return response


#Refresh Token Rotation
@app.route('/refresh',methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    jwt_data = get_jwt()

    # Blacklist old refresh token
    db.session.add(TokenBlocklist(
        jti=jwt_data["jti"],
        token_type="refresh",
        expires_at=datetime.fromtimestamp(jwt_data["exp"], timezone.utc)
    ))
    db.session.commit()

    username=get_jwt_identity()
    new_access_token = create_access_token(identity=username)
    new_refresh_token = create_refresh_token(identity=username)

    response = jsonify(message='New access token generated')
    set_access_cookies(response, new_access_token)
    set_refresh_cookies(response, new_refresh_token)

    return response


#Token Blocklist checking
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]

    token = TokenBlocklist.query.filter_by(jti=jti).first()
    return token is not None


#POST
@app.route('/users', methods=['POST'])
@jwt_required()
def create_user():
    data = request.json
    user = User(name=data['name'], email=data['email'])
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


#GET (ALL)
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])


#GET(SINGLE DATA)
@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_dict())


#UPDATE
@app.route('/users/<int:id>', methods=['PUT'])
@jwt_required()
def update_user(id):
    user = User.query.get_or_404(id)
    data = request.json

    # user.name in brackets is for default value . If no value is specified then old value will be used
    user.name = data.get('name', user.name)
    user.email = data.get('email', user.email)

    db.session.commit()
    return jsonify(user.to_dict())


#DELETE
@app.route('/users/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_user(id):
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted successfully"})


#Logout (Token Blacklisting)
@app.route('/logout', methods=['DELETE'])
@jwt_required(verify_type=False)
def logout():
    jwt_data=get_jwt()
    jti = jwt_data["jti"]
    token_type = jwt_data["type"]
    expires = datetime.fromtimestamp(jwt_data["exp"],timezone.utc)

    blocked_token= TokenBlocklist(jti=jti, token_type=token_type, expires_at=expires)

    db.session.add(blocked_token)
    db.session.commit()

    response=jsonify(message='Logout done successfully')
    unset_jwt_cookies(response)

    return response


#Data cleanup method - runs in background ( celery- It is an open-sourced distributed task queue system
# which is used to run scheduled tasks outside the main application flow )
#A job has to be set so that expired tokens will be deleted periodically from the db for increasing scalability.

def cleanup_expired_tokens():
    now = datetime.now(timezone.utc)

    TokenBlocklist.query.filter(
        TokenBlocklist.expires_at < now
    ).delete(synchronize_session=False)

    db.session.commit()



if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
