import os
import json

from sqlalchemy import Column, String, Integer, Boolean 
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

database_name = 'okr_test_local'
database_path = "postgresql://{}/{}".format('localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''

def setup_db(app, database_path=database_path):
    app.config['SQLALCHEMY_DATABASE_URI'] = database_path
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    # db.create_all()
    migrate = Migrate(app, db)


'''
Person
'''

class Person(db.Model):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable = False)
    first_name = Column(String, nullable = False)
    is_boss = Column(Boolean, nullable = False)

    objectives = db.relationship('Objective', backref = 'person_ref', lazy = True, cascade = 'all, delete-orphan')

    def __init__(self, name, first_name, is_boss=False):
        self.name = name
        self.first_name = first_name
        self.is_boss = is_boss
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'first_name': self.first_name,
            'is_boss': self.is_boss
        }



'''
Objective
'''

class Objective(db.Model):
    __tablename__ = 'objectives'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable = False)
    person = db.Column(Integer, db.ForeignKey('persons.id', ondelete="CASCADE"), nullable = False)

    requirements = db.relationship('Requirement', backref = 'objectives_ref', lazy = True, cascade = 'all, delete-orphan')

    @property
    def get_name(self):
        return ", ".join([self.person_ref.name, self.person_ref.first_name])

    def __init__(self, description, person):
        self.description = description
        self.person = person

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'description': self.description,
            'person': self.person,
            'complete_name': self.get_name,
        }


'''
Requirements
'''

class Requirement(db.Model):
    __tablename__ = 'requirements'

    id = Column(Integer, primary_key=True)
    description = Column(String, nullable = False)
    is_met = Column(Boolean, nullable = False)
    objective = db.Column(Integer, db.ForeignKey('objectives.id', ondelete="CASCADE"), nullable = False)

    def __init__(self, description, objective):
        self.description = description
        self.objective = objective
        self.is_met = False

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'is_met': self.is_met,
            'description': self.description,
            'objective_id': self.objective,
            'objective_description': self.objectives_ref.description,
        }