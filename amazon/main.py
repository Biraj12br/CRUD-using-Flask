from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required,get_jwt_identity,create_access_token
import mysql.connector

app=Flask(__name__)
jwt=JWTManager(app)

#JWT Configuration
app.config['JWT_SECRET_KEY']='super_secret_key'
app.config['JWT_TOKEN_LOCATION']=['headers','cookies']

#Database Connection
db=mysql.connector.connect(
    host='localhost',
    user='root',
    password='Biraj351',
    db='flask'
)

user={'Biraj':{'password':"secret_key"}}

#JWT token creation
#POST
@app.route('/login',methods=['POST'])
def login():
    username=request.json.get('username')
    password=request.json.get('password')

    if username not in user or user[username]["password"] != password :
        return jsonify("Wrong username or password")

    access_token= create_access_token(identity=username)
    return jsonify(access_token=access_token)

#GET
@app.route('/get_info/<id>',methods=['GET'])
def get_info(id):
    cursor=db.cursor(dictionary=True)
    cursor.execute('select * from sales where product_id = %s',(id,))
    data=cursor.fetchall()
    cursor.close()
    return jsonify(required_data=data)

#PUT
@app.route('/update_record_list',methods=['PUT'])
@jwt_required()
def update_record():
    data=request.json
    cursor=db.cursor()
    for record in data:
        details=record.get('details')
        product_id=record.get('id')
        cursor.execute('update sales set about_product = %s where product_id = %s', (details, product_id))
    db.commit()
    cursor.close()

    return jsonify({'message': 'Data Updated'})

#DELETE
@app.route('/delete_record_list',methods=['DELETE'])
@jwt_required()
def delete_data():
    data=request.json
    cursor=db.cursor()
    for record in data:
        id=record.get('id')
        cursor.execute('delete from sales where product_id=%s',(id,))
    db.commit()
    cursor.close()
    return jsonify({'message':'Data Deleted'})


if __name__ == '__main__':
    app.run(debug=True)