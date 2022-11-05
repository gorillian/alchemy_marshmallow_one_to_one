import json
import psycopg2
from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow

from db import *
from organizations import Organizations, organization_schema, organizations_schema
from users import Users, user_schema, users_schema

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://ian@localhost:5432/alchemy"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app, db)

ma = Marshmallow(app)

# conn = psycopg2.connect("dbname='usermgt' user='ian' host='localhost'")
# cursor = conn.cursor()


def create_all():
  with app.app_context():
    print("Creating tables...")
    db.create_all()
    print("All done!")




@app.route('/user/add', methods=['POST'])
def user_add():
  post_data = request.json
  if not post_data:
    post_data = request.post
  
  first_name = post_data.get('first_name')
  last_name = post_data.get('last_name')
  email = post_data.get('email')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  org_id = post_data.get('org_id')
  active = post_data.get('active')

  return add_user(first_name, last_name, email, phone, city, state, org_id, active)

  
def add_user(first_name, last_name, email, phone, city, state, org_id, active):
  new_user = Users(first_name, last_name, email, phone, city, state, org_id, active)

  db.session.add(new_user)

  db.session.commit()

  return jsonify(user_schema.dump(new_user)), 201


@app.route('/users/get', methods=['GET'])
def get_all_active_users():
  users = db.session.query(Users).filter(Users.active == True).all()

  return jsonify(users_schema.dump(users)), 200

@app.route('/user/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
  user_by_id = db.session.query(Users).filter(Users.user_id == user_id).one()

  return jsonify(user_schema.dump(user_by_id)), 200

@app.route('/users/activate/<user_id>')
def activate_user(user_id):
  user_data = db.session.query(Users).filter(Users.user_id == user_id).first()
  if user_data:
    user_data.active = True
    db.session.commit()
    return jsonify(user_schema.dump(user_data)), 200

@app.route('/users/deactivate/<user_id>')
def deactivate_user(user_id):
  user_data = db.session.query(Users).filter(Users.user_id == user_id).first()
  if user_data:
    user_data.active = False
    db.session.commit()
  return jsonify(user_schema.dump(user_data)), 200

@app.route('/users/delete/<user_id>')
def delete_user(user_id):
  delete_user = db.session.query(Users).filter(Users.user_id == user_id).delete()
  db.session.commit()
  return jsonify(user_schema.dump(delete_user)), 200


@app.route('/users/update/<user_id>', methods=['POST', 'PUT'])
def user_update(user_id):
  user_to_update = (db.session.query(Users).filter(Users.user_id == user_id)).first()

  if not user_to_update:
    return jsonify("user with id not found", 404)

  post_data = request.json
  if not post_data:
    post_data = request.form
  
  if post_data.get('first_name'):
    user_to_update.first_name = post_data.get('first_name')
  if post_data.get('last_name'):
    user_to_update.last_name = post_data.get('last_name')
  if post_data.get('email'):
    user_to_update.email = post_data.get('email')
  if post_data.get('phone'):
    user_to_update.phone = post_data.get('phone')
  if post_data.get('city'):
    user_to_update.city = post_data.get('city')
  if post_data.get('state'):
    user_to_update.state = post_data.get('state')
  if post_data.get('org_id'):
    user_to_update.org_id = post_data.get('org_id')
  if post_data.get('active'):
    user_to_update.active = post_data.get('active')

  db.session.commit()

  return jsonify(user_schema.dump(user_to_update)), 200 



@app.route('/org/add', methods=["POST"])
def org_add():
  post_data = request.json
  if not post_data:
    post_data = request.form
  name = post_data.get('name')
  phone = post_data.get('phone')
  city = post_data.get('city')
  state = post_data.get('state')
  active = post_data.get('active')

  return add_org(name, phone, city, state, active)


def add_org(name, phone, city, state, active):
  new_org = Organizations(name, phone, city, state, active)

  db.session.add(new_org)
  db.session.commit()

  return jsonify(organization_schema.dump(new_org)), 200

@app.route('/orgs/get', methods = ['GET'])
def get_all_active_orgs():
  results = db.session.query(Organizations).filter(Organizations.active==True)
  
  return jsonify(organizations_schema.dump(results)), 200

@app.route('/org/<org_id>', methods=['GET'])
def get_org_by_id(org_id):
  org_by_id = db.session.query(Organizations).filter(Organizations.org_id == org_id).one()

  return jsonify(organization_schema.dump(org_by_id)), 200

@app.route('/org/activate/<org_id>')
def activate_org(org_id):
  org_data = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  if org_data:
    org_data.active = True
    db.session.commit()
  return jsonify(organization_schema.dump(org_data)), 200

@app.route('/org/deactivate/<org_id>')
def deactivate_org(org_id):
  org_data = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  if org_data:
    org_data.active = False
    db.session.commit()
  return jsonify(organization_schema.dump(org_data)), 200

@app.route('/org/delete/<org_id>')
def delete_org(org_id):
  delete_org = db.session.query(Organizations).filter(Organizations.org_id == org_id).delete()
  db.session.commit()
  return jsonify(organization_schema.dump(delete_org)), 200
  
@app.route('/org/update/<org_id>', methods = ['POST', 'PUT'])
def org_update(org_id):
  organization = db.session.query(Organizations).filter(Organizations.org_id == org_id).first()
  
  if not organization:
    return jsonify(f"Org with id {org_id} is not found"), 404

  post_data = request.json
  if not post_data:
    post_data = request.form

  if post_data.get("name"):
    organization.name = post_data.get("name")
  if post_data.get("phone"):
    organization.phone = post_data.get("phone")
  if post_data.get("city"):
    organization.city = post_data.get("city")
  if post_data.get("state"):
    organization.state = post_data.get("state")
  if "active" in post_data:
    organization.active = post_data.get("active")

  db.session.commit()

  return jsonify(organization_schema.dump(organization)), 200
  

if __name__ == '__main__':
  create_all()
  app.run(port=8089)
