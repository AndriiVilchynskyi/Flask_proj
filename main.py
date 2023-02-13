import datetime

from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String, Integer, Float, Date, CheckConstraint
from flask_marshmallow import Marshmallow
from datetime import date
import os

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "order_list.db")

db = SQLAlchemy(app)
ma = Marshmallow(app)


@app.route("/orders")
def orders():
    orders_list = Order.query.all()
    result = orders_schema.dump(orders_list)
    return jsonify(result)


@app.route("/clients", methods=["GET"])
def clients():
    clients_list = Client.query.all()
    result = clients_schema.dump(clients_list)
    return jsonify(result)


@app.cli.command("db_create")
def db_create():
    db.create_all()
    print("Database created!")


@app.cli.command("db_drop")
def db_drop():
    db.drop_all()
    print("Database dropped!")


@app.cli.command("db_seed")
def db_seed():
    Andrii = Client(first_name="Andrii",
                    last_name="Vilchynskyi",
                    registration_date=datetime.datetime.now(),
                    number_of_orders=1
                    )
    Igor = Client(first_name="Igor",
                  last_name="Nagirniy",
                  registration_date=datetime.datetime.now(),
                  number_of_orders=3
                  )
    Ostap = Client(first_name="Ostap",
                   last_name="Shtogrin",
                   registration_date=datetime.datetime.now(),
                   number_of_orders=2
                   )

    order1 = Order(id=412,
                   car_number='ab241',
                   add_date=datetime.datetime.now(),
                   rental_time=2,
                   car_rental_cost=85.00)
    order1.calculate_total_cost()

    order2 = Order(id=532,
                   car_number='ac4123',
                   add_date=datetime.datetime.now(),
                   rental_time=3,
                   car_rental_cost=77.00)
    order2.calculate_total_cost()

    db.session.add(order1)
    db.session.add(order2)

    db.session.add(Andrii)
    db.session.add(Igor)
    db.session.add(Ostap)
    db.session.commit()
    print("Database seeded!")


@app.route('/orders/add', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        car_number = request.form['car_number']
        client_passport_number = request.form['client_passport_number']
        rental_time = int(request.form['rental_time'])
        car_rental_cost = float(request.form['car_rental_cost'])

        order = Order(car_number=car_number,
                      client_passport_number=client_passport_number,
                      rental_time=rental_time,
                      car_rental_cost=car_rental_cost)
        order.calculate_total_cost()

        db.session.add(order)
        db.session.commit()

        return redirect(url_for('orders_list'))
    return render_template('add_order.html')


@app.route('/clients_list')
def clients_list():
    clients_html = Client.query.all()
    return render_template('clients_list.html', clients_html=clients_html)


@app.route("/orders_list")
def orders_list():
    orders_html = Order.query.all()
    return render_template("orders_list.html", orders_html=orders_html)


# database models

class Order(db.Model):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True)
    car_number = Column(String, unique=True)
    add_date = Column(Date, default=date.today, nullable=False)
    rental_time = Column(Integer, nullable=False)
    car_rental_cost = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)

    __table_args__ = (
        CheckConstraint(rental_time >= 1, name='minimal_rental_time'),
    )

    def calculate_total_cost(self):
        self.total_cost = self.rental_time * self.car_rental_cost


class Client(db.Model):
    __tablename__ = "clients"
    client_id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    registration_date = Column(Date, default=date.today, nullable=False)
    number_of_orders = Column(Integer, default=0)

    def __repr__(self):
        return '<Client {} {}>'.format(self.first_name, self.last_name)


class ClientSchema(ma.Schema):
    class Meta:
        fields = ("client_id", "first_name", "last_name", "registration_date", "number_of_orders")


class OrderSchema(ma.Schema):
    class Meta:
        fields = ("id", "car_number", "add_date", "rental_time", "car_rental_cost", "total_cost")


client_schema = ClientSchema()
clients_schema = ClientSchema(many=True)

order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)

if __name__ == "__main__":
    app.run()
