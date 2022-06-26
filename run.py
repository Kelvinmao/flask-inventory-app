import binascii
import enum
import hashlib
import os

from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy

from flask_login import (
    current_user,
    login_required,
    login_user,
    logout_user,
    LoginManager, UserMixin
)
from flask_wtf import FlaskForm
from flask import session
from wtforms import TextAreaField, PasswordField
from wtforms.validators import InputRequired, Email, DataRequired
from collections import defaultdict
from datetime import datetime, timedelta
from flask_cors import CORS, cross_origin
from flask_session import Session
import functools


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
# app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['LOGIN_DISABLED'] = False
db = SQLAlchemy(app)
# Session(app)
# CORS(app)
app.config.update(SESSION_COOKIE_SAMESITE="None", SESSION_COOKIE_SECURE=True)

login_manager = LoginManager()
login_manager.init_app(app)
# login_manager.login_view = 'login'

Hazards = ('Flammable', 'Irritant')
TRUE_SYNONYM = ['Yes']
# SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = 'S#perS3crEt_007'


@login_manager.user_loader
def user_loader(id):
    return User.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = User.query.filter_by(username=username).first()
    return user if user else None


class User(db.Model, UserMixin):
    __tablename__ = 'User'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True)
    email = db.Column(db.String, unique=True)
    password = db.Column(db.LargeBinary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


class Chemical(db.Model):
    __tablename__ = 'chemicals'

    chemical_id = db.Column(db.String, primary_key=True)
    cas_number = db.Column(db.String, default='00-00-0')
    container_size = db.Column(db.Float, default=0.0)
    container_size_unit = db.Column(db.String, default='L')
    room_number = db.Column(db.String, default='W6-050')
    storage_name = db.Column(db.String, default='Flammable Cabinet 1')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    location = db.Column(db.String, default='Cabinet')
    peroxide_former_bool = db.Column(db.Boolean, default=True)
    expiration_date = db.Column(db.DateTime, default=datetime.utcnow())
    main_hazards = db.Column(db.String, default=','.join(Hazards))
    TDG_class = db.Column(db.String, default='TDG-3')
    Storage_category = db.Column(db.String, default='Flammable')
    Freeze_bool = db.Column(db.Boolean, default=True)
    Manufacturer = db.Column(db.String, default='Sigma')
    Remarks = db.Column(db.String, default='NA')


class Product(db.Model):
    __tablename__ = 'products'
    product_id = db.Column(db.String(200), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Product %r>' % self.product_id


class Location(db.Model):
    __tablename__ = 'locations'
    location_id = db.Column(db.String(200), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Location %r>' % self.location_id


class ChemicalLocation(db.Model):
    __tablename__ = 'chemicalLocations'

    chemical_location_id = db.Column(db.String(200), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<ChemicalLocation %r>' % self.chemical_location_id


class Storage(db.Model):
    __tablename__ = 'storages'

    storage_id = db.Column(db.String(200), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Storage %r>' % self.storage_id


class ProductMovement(db.Model):
    __tablename__ = 'productmovements'

    movement_id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.product_id'))
    qty = db.Column(db.Integer)
    from_location = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    to_location = db.Column(db.Integer, db.ForeignKey('locations.location_id'))
    movement_time = db.Column(db.DateTime, default=datetime.utcnow)

    product = db.relationship('Product', foreign_keys=product_id)
    fromLoc = db.relationship('Location', foreign_keys=from_location)
    toLoc = db.relationship('Location', foreign_keys=to_location)

    def __repr__(self):
        return '<ProductMovement %r>' % self.movement_id


class MainHazards(db.Model):
    __tablename__ = 'hazards'

    hazard_id = db.Column(db.String(300), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Hazard %r>' % self.hazard_id


class StorageCategory(db.Model):
    __tablename__ = 'storageCategories'

    storage_category_id = db.Column(db.String(300), primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<StorageCategory %r>' % self.storage_category_id


## login and registration
class LoginForm(FlaskForm):
    username = TextAreaField('Username', id='username_login', validators=[DataRequired()])
    password = PasswordField('Password', id='pwd_login', validators=[DataRequired()])


class CreateAccountForm(FlaskForm):
    username = TextAreaField('Username', id='username_create', validators=[DataRequired()])
    email = TextAreaField('Email', id='email_create', validators=[DataRequired(), Email()])
    password = PasswordField('Password', id='pwd_create', validators=[DataRequired()])


def hash_pass(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return salt + pwdhash  # return bytes


def verify_pass(provided_password, stored_password):
    """Verify a stored password against one provided by user"""
    stored_password = stored_password.decode('ascii')
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_password.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password


@app.route('/')
# @cross_origin(supports_credentials=True)
def route_default():
    return redirect(url_for('chemicalBalanceReport'))


@app.route('/login', methods=['GET', 'POST'])
# @cross_origin(supports_credentials=True)
def login():
    login_form = LoginForm(request.form)
    if 'login' in request.form:

        # read form data
        username = request.form['username']
        password = request.form['password']

        # Locate user
        user = User.query.filter_by(username=username).first()

        # Check the password
        if user and verify_pass(password, user.password):
            login_user(user, duration=timedelta(minutes=30))
            return redirect(url_for('route_default'))

        # Something (user or pass) is not ok
        return render_template('accounts/login.html', msg='Wrong user or password', form=login_form)

    if not current_user.is_authenticated:
        return render_template('accounts/login.html',
                               form=login_form)
    return redirect(url_for('index'))


@app.route('/logout', methods=['POST', 'GET'])
# @cross_origin(supports_credentials=True)
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
# @cross_origin(supports_credentials=True)
def register():
    login_form = LoginForm(request.form)
    create_account_form = CreateAccountForm(request.form)
    if 'register' in request.form:

        username = request.form['username']
        email = request.form['email']

        # Check username exists
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Username already registered',
                                   success=False,
                                   form=create_account_form)

        # Check email exists
        user = User.query.filter_by(email=email).first()
        if user:
            return render_template('accounts/register.html',
                                   msg='Email already registered',
                                   success=False,
                                   form=create_account_form)

        # else we can create the user
        user = User(**request.form)
        db.session.add(user)
        db.session.commit()

        return render_template('accounts/register.html',
                               msg='User created please <a href="/login">login</a>',
                               success=True,
                               form=create_account_form)

    else:
        return render_template('accounts/register.html', form=create_account_form)


@app.route('/index', methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def index():
    if (request.method == "POST") and ('location_name' in request.form):
        location_name = request.form["location_name"]
        new_location = Location(location_id=location_name)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect("/index.html")

        except:
            return "There Was an issue while add a new Location"
    else:
        chemicals = Chemical.query.order_by(Chemical.date_created).all()
        locations = Location.query.order_by(Location.date_created).all()
        return render_template("index.html", chemicals=chemicals, locations=locations)


# View Starts
@app.route('/locations/', methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def viewLocation():
    print(session)
    if (request.method == "POST") and ('location_name' in request.form):
        location_name = request.form["location_name"]
        new_location = Location(location_id=location_name)

        try:
            db.session.add(new_location)
            db.session.commit()
            return redirect("/locations/")

        except:
            locations = Location.query.order_by(Location.date_created).all()
            return "There Was an issue while add a new Location"
    else:
        locations = Location.query.order_by(Location.date_created).all()
        return render_template("locations.html", locations=locations)


@app.route('/chemical-locations/', methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def viewChemicalLocation():
    print(session)
    if (request.method == "POST") and ('chemical_location_name' in request.form):
        chemical_location_name = request.form["chemical_location_name"]
        new_chemical_location = ChemicalLocation(chemical_location_id=chemical_location_name)
        # print(new_storage)
        try:
            db.session.add(new_chemical_location)
            db.session.commit()
            return redirect("/chemical-locations/")
        except:
            chemical_locations = ChemicalLocation.query.order_by(ChemicalLocation.date_created).all()
            return "There Was an issue while add a new Location"
    else:
        chemical_locations = ChemicalLocation.query.order_by(ChemicalLocation.date_created).all()
        return render_template("chemical_locations.html", chemical_locations=chemical_locations)


@app.route('/chemicals/', methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def viewChemicals():
    print(session)
    if (request.method == "POST") and ('chemical_name' in request.form):
        chemical_name = request.form["chemical_name"]
        new_chemical = Chemical(chemical_id=chemical_name)
        try:
            db.session.add(new_chemical)
            db.session.commit()
            return redirect("/chemicals/")

        except:
            chemicals = Chemical.query.order_by(Chemical.date_created).all()
            return "There Was an issue while add a new Product"
    else:
        chemicals = Chemical.query.order_by(Chemical.date_created).all()
        return render_template("chemicals.html", chemicals=chemicals)


@app.route('/storages/', methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def viewStorage():
    if (request.method == "POST") and ('storage_name' in request.form):
        storage_name = request.form["storage_name"]
        new_storage = Storage(storage_id=storage_name)
        # print(new_storage)
        try:
            db.session.add(new_storage)
            db.session.commit()
            return redirect("/storages/")

        except:
            storage_name = Storage.query.order_by(Storage.date_created).all()
            return "There Was an issue while add a new Storage"
    else:
        storages = Storage.query.order_by(Storage.date_created).all()
        return render_template("storages.html", storages=storages)


@app.route('/hazards/', methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def viewHazard():
    if (request.method == "POST") and ('hazard_name' in request.form):
        hazard_name = request.form["hazard_name"]
        new_hazard = MainHazards(hazard_id=hazard_name)
        # print(new_storage)
        try:
            db.session.add(new_hazard)
            db.session.commit()
            return redirect("/hazards/")

        except:
            hazard_name = MainHazards.query.order_by(MainHazards.date_created).all()
            return "There Was an issue while add a new Storage"
    else:
        hazards = MainHazards.query.order_by(MainHazards.date_created).all()
        return render_template("hazards.html", hazards=hazards)


@app.route('/storage-categories/', methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def viewStorageCategory():
    if (request.method == "POST") and ('storage_category_name' in request.form):
        storage_category_name = request.form["storage_category_name"]
        new_storage_category = StorageCategory(storage_category_id=storage_category_name)

        try:
            db.session.add(new_storage_category)
            db.session.commit()
            return redirect("/storage-categories/")

        except:
            storage_category_name = StorageCategory.query.order_by(StorageCategory.date_created).all()
            return "There Was an issue while add a new Storage"
    else:
        storage_categories = StorageCategory.query.order_by(StorageCategory.date_created).all()
        return render_template("storage-categories.html", storage_categories=storage_categories)
# View Ends


# Update Starts
@app.route("/update-chemical/<name>", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def updateChemical(name):
    chemical = Chemical.query.get_or_404(name)
    old_chemical = chemical.chemical_id
    location = Location.query.all()
    chemical_location = ChemicalLocation.query.all()
    storages = Storage.query.all()
    hazards = MainHazards.query.all()
    storage_categories = StorageCategory.query.all()

    if request.method == "POST":
        chemical.chemical_id = request.form['chemical_name']
        # ImmutableMultiDict([('chemical_name', 'iMac'), ('cas_number', '00-00-0'),
        # ('container_size', '0.0'), ('room_number', 'W6-050'),
        # ('storage_name', 'Flammable Cabinet 1'),
        # ('data_created', 'Flammable Cabinet 1'),
        # ('location', 'Cabinet'), ('peroxide_former_bool', 'Yes'),
        # ('expiration_date', '2022-06-13'), ('main_hazards_1', 'Flammable'),
        # ('main_hazards_2', 'Irritant'), ('TDG_class', 'TDG-3'),
        # ('storage_category_1', 'Flammable'), ('freeze_bool', 'Yes'),
        # ('manufacturer', 'Sigma'), ('remarks', 'NA')])

        chemical.cas_number = request.form['cas_number']
        chemical.container_size = request.form['container_size']
        chemical.container_size_unit = request.form['container_size_unit']
        chemical.room_number = request.form['room_number']
        chemical.storage_name = request.form['storage_name']
        chemical.date_created = datetime.strptime(request.form['data_created'], '%Y-%m-%d')
        chemical.location = request.form['chemical_location']
        chemical.peroxide_former_bool = request.form['peroxide_former_bool'] in TRUE_SYNONYM
        chemical.expiration_date = datetime.strptime(request.form['expiration_date'], '%Y-%m-%d')
        chemical.main_hazards = ','.join(tuple(request.form.getlist("main_hazards")))
        chemical.TDG_class = request.form['TDG_class']
        chemical.Storage_category = ','.join(tuple(request.form.getlist("storage_category")))
        chemical.Freeze_bool = request.form['freeze_bool'] in TRUE_SYNONYM
        chemical.Manufacturer = request.form['manufacturer']
        chemical.Remarks = request.form['remarks']

        try:
            db.session.commit()
            updateProductInMovements(old_chemical, request.form['chemical_name'])
            return redirect("/chemicals/")

        except Exception as e:
            print(e)
            return "There was an issue while updating the Chemical"
    else:
        return render_template("update-chemical.html", chemical=chemical,
                               location=location,
                               chemical_location=chemical_location,
                               storages=storages,
                               hazards=hazards,
                               storage_categories=storage_categories
                               )


@app.route("/update-location/<name>", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def updateLocation(name):
    location = Location.query.get_or_404(name)
    old_location = location.location_id

    if request.method == "POST":
        location.location_id = request.form['location_name']

        try:
            db.session.commit()
            updateLocationInMovements(
                old_location, request.form['location_name'])
            return redirect("/locations/")

        except:
            return "There was an issue while updating the Location"
    else:
        return render_template("update-location.html", location=location)


@app.route("/update-chemical-location/<name>", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def updateChemicalLocation(name):
    chemical_location = ChemicalLocation.query.get_or_404(name)
    old_chemical_location = chemical_location.chemical_location_id

    if request.method == "POST":
        chemical_location.chemical_location_id = request.form['chemical_location_name']

        try:
            db.session.commit()
            updateChemicalLocationInMovements(
                old_chemical_location, request.form['chemical_location_name'])
            return redirect("/chemical-locations/")

        except:
            return "There was an issue while updating the Location"
    else:
        return render_template("update-chemical-location.html", chemical_location=chemical_location)


@app.route("/update-storage/<name>", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def updateStorage(name):
    storage = Storage.query.get_or_404(name)
    old_storage = storage.storage_id

    if request.method == "POST":
        storage.storage_id = request.form['storage_name']

        try:
            db.session.commit()
            updateStorageInMovements(
                old_storage, request.form['storage_name'])
            return redirect("/storages/")

        except:
            return "There was an issue while updating the Location"
    else:
        return render_template("update-storage.html", storage=storage)


def updateHazardInMovements(old_hazard, param):
    pass


@app.route("/update-hazard/<name>", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def updateHazard(name):
    hazard = MainHazards.query.get_or_404(name)
    old_hazard = hazard.hazard_id

    if request.method == "POST":
        hazard.hazard_id = request.form['hazard_name']

        try:
            db.session.commit()
            updateHazardInMovements(
                old_hazard, request.form['hazard_name'])
            return redirect("/hazards/")

        except:
            return "There was an issue while updating the Location"
    else:
        return render_template("update-hazard.html", hazard=hazard)


def updateStorageCategoryInMovements(old_storage_category, param):
    pass


@app.route("/update-storage-category/<name>", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def updateStorageCategory(name):
    storage_category = StorageCategory.query.get_or_404(name)
    old_storage_category = storage_category.storage_category_id

    if request.method == "POST":
        storage_category.storage_category_id = request.form['storage_category_name']

        try:
            db.session.commit()
            updateStorageCategoryInMovements(
                old_storage_category, request.form['storage_category_name'])
            return redirect("/storage-categories/")

        except:
            return "There was an issue while updating the Storage Category"
    else:
        return render_template("update-storage-category.html", storage_category=storage_category)
# Update Ends


# Delete Starts
@app.route("/delete-storage/<name>")
# @cross_origin(supports_credentials=True)
@login_required
def deleteStorage(name):
    storage_to_delete = Storage.query.get_or_404(name)

    try:
        db.session.delete(storage_to_delete)
        db.session.commit()
        return redirect("/storages/")
    except:
        return "There was an issue while deleteing the Storage"


@app.route("/delete-hazard/<name>")
# @cross_origin(supports_credentials=True)
@login_required
def deleteHazard(name):
    hazard_to_delete = MainHazards.query.get_or_404(name)

    try:
        db.session.delete(hazard_to_delete)
        db.session.commit()
        return redirect("/hazards/")
    except:
        return "There was an issue while deleteing the Hazard"


@app.route("/delete-storage-category/<name>")
# @cross_origin(supports_credentials=True)
@login_required
def deleteStorageCategory(name):
    storage_category_to_delete = StorageCategory.query.get_or_404(name)

    try:
        db.session.delete(storage_category_to_delete)
        db.session.commit()
        return redirect("/storage-categories/")
    except:
        return "There was an issue while deleteing the Storage Category"


@app.route("/delete-product/<name>")
# @cross_origin(supports_credentials=True)
@login_required
def deleteProduct(name):
    product_to_delete = Product.query.get_or_404(name)

    try:
        db.session.delete(product_to_delete)
        db.session.commit()
        return redirect("/products/")
    except:
        return "There was an issue while deleteing the Product"


@app.route("/delete-chemical/<name>")
# @cross_origin(supports_credentials=True)
@login_required
def deleteChemical(name):
    chemical_to_delete = Chemical.query.get_or_404(name)

    try:
        db.session.delete(chemical_to_delete)
        db.session.commit()
        return redirect("/chemicals/")
    except:
        return "There was an issue while deleteing the Chemical"


@app.route("/delete-location/<name>", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def deleteLocation(name):
    location_to_delete = Location.query.get_or_404(name)

    try:
        db.session.delete(location_to_delete)
        db.session.commit()
        return redirect("/locations/")
    except:
        return "There was an issue while deleteing the Location"


@app.route("/delete-chemical-location/<name>")
# @cross_origin(supports_credentials=True)
@login_required
def deleteChemicalLocation(name):
    chemical_location_to_delete = ChemicalLocation.query.get_or_404(name)

    try:
        db.session.delete(chemical_location_to_delete)
        db.session.commit()
        return redirect("/chemical-locations/")
    except:
        return "There was an issue while deleteing the Chemical Location"


@app.route("/delete-movement/<int:id>")
# @cross_origin(supports_credentials=True)
@login_required
def deleteMovement(id):
    movement_to_delete = ProductMovement.query.get_or_404(id)

    try:
        db.session.delete(movement_to_delete)
        db.session.commit()
        return redirect("/movements/")
    except:
        return "There was an issue while deleteing the Prodcut Movement"


# Delete Ends


def updateChemicalLocationInMovements(old_chemical_location, param):
    pass


@app.route("/chemical-balance/", methods=["GET"])
def chemicalBalanceReport():
    chemicals = Chemical.query.order_by(Chemical.date_created).all()
    return render_template("chemical-balance.html", chemicals=chemicals)


@app.route("/chemical-balance/<name>", methods=["GET"])
def ChemicalDetail(name):
    chemical = Chemical.query.get_or_404(name)
    return render_template("chemical-detail.html", chemical=chemical)


@app.route("/movements/get-from-locations/", methods=["POST"])
def getLocations():
    product = request.form["productId"]
    location = request.form["location"]
    locationDict = defaultdict(lambda: defaultdict(dict))
    locations = ProductMovement.query. \
        filter(ProductMovement.product_id == product). \
        filter(ProductMovement.to_location != ''). \
        add_columns(ProductMovement.from_location, ProductMovement.to_location, ProductMovement.qty). \
        all()

    for key, location in enumerate(locations):
        if (locationDict[location.to_location] and locationDict[location.to_location]["qty"]):
            locationDict[location.to_location]["qty"] += location.qty
        else:
            locationDict[location.to_location]["qty"] = location.qty

    return locationDict


# Duplicate Starts
@app.route("/dub-locations/", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def getDublicate():
    location = request.form["location"]
    locations = Location.query. \
        filter(Location.location_id == location). \
        all()
    # print(locations)
    if locations:
        return {"output": False}
    else:
        return {"output": True}


@app.route("/dub-chemical-locations/", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def getChemicalLocationDublicate():
    chemical_location = request.form["chemical_location"]
    chemical_locations = ChemicalLocation.query. \
        filter(ChemicalLocation.chemical_location_id == chemical_location). \
        all()
    if chemical_locations:
        return {"output": False}
    else:
        return {"output": True}


@app.route("/dub-storages/", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def getStorageDublicate():
    # print(request.form)
    storage = request.form["storage"]
    storage = Storage.query. \
        filter(Storage.storage_id == storage). \
        all()
    if storage:
        return {"output": False}
    else:
        return {"output": True}


@app.route("/dub-hazards/", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def getHazardDublicate():
    # print(request.form)
    hazard = request.form["hazard"]
    hazard = MainHazards.query. \
        filter(MainHazards.hazard_id == hazard). \
        all()
    if hazard:
        return {"output": False}
    else:
        return {"output": True}


@app.route("/dub-storage-categories/", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def getStorageCategoryDublicate():
    storage_category = request.form["storage_category"]
    storage_category = StorageCategory.query. \
        filter(StorageCategory.storage_category_id == storage_category). \
        all()
    if storage_category:
        return {"output": False}
    else:
        return {"output": True}


@app.route("/dub-products/", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def getPDublicate():
    product_name = request.form["product_name"]
    products = Product.query. \
        filter(Product.product_id == product_name). \
        all()
    # print(products)
    if products:
        return {"output": False}
    else:
        return {"output": True}


@app.route("/dub-chemicals/", methods=["POST", "GET"])
# @cross_origin(supports_credentials=True)
@login_required
def getChemDuplicate():
    chemical_name = request.form["chemical_name"]
    chemicals = Chemical.query. \
        filter(Chemical.chemical_id == chemical_name). \
        all()
    # print(chemicals)
    if chemicals:
        return {"output": False}
    else:
        return {"output": True}


# Duplicate Ends

def updateLocationInMovements(oldLocation, newLocation):
    movement = ProductMovement.query.filter(ProductMovement.from_location == oldLocation).all()
    movement2 = ProductMovement.query.filter(ProductMovement.to_location == oldLocation).all()
    for mov in movement2:
        mov.to_location = newLocation
    for mov in movement:
        mov.from_location = newLocation

    db.session.commit()


def updateStorageInMovements(oldStorage, newStorage):
    pass


def updateProductInMovements(oldProduct, newProduct):
    movement = ProductMovement.query.filter(ProductMovement.product_id == oldProduct).all()
    for mov in movement:
        mov.product_id = newProduct

    db.session.commit()


if __name__ == "__main__":
    db.create_all()
    app.run(debug=False)
