import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
import json

#HERE CONFIG DATABASE NAME 
database_name = "trivia"
#HERE PUT NAME OF YOUR DATABASE AND PASSWORD AND YOR SERVER NAME
database_path = "postgres://{}:{}@{}/{}".format('postgres', 'soso','localhost:5432', database_name)

 #CONFIG YOUR DATA BASE
db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
#FUCTION FOR CONFIG YOUR DATA BASE 
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

'''
Question

'''

# CREATE CLASS FOR YOUR  ALL QUESTIONS
class Question(db.Model):  
  __tablename__ = 'questions'

  id = Column(Integer, primary_key=True)
  question = Column(String)
  answer = Column(String)
  category = Column(String)
  difficulty = Column(Integer)

  def __init__(self, question, answer, category, difficulty):
    self.question = question
    self.answer = answer
    self.category = category
    self.difficulty = difficulty

  #CREATE FUCTION INSERT DATA

  def insert(self):
    db.session.add(self)
    db.session.commit()

  
  #CRETA FUCTION FOR UPDATE DATA
  def update(self):
    db.session.commit()

  #DELET DATA
  def delete(self):
    db.session.delete(self)
    db.session.commit()
  
  #FORMAT DATA TO DISPLAY IT
  def format(self):
    return {
      'id': self.id,
      'question': self.question,
      'answer': self.answer,
      'category': self.category,
      'difficulty': self.difficulty
    }

'''
Category

'''
#CREATE CLASS FOR ALL CATEGORY
class Category(db.Model):  
  __tablename__ = 'categories'

  id = Column(Integer, primary_key=True)
  type = Column(String)

  def __init__(self, type):
    self.type = type

  def format(self):
    return {
      'id': self.id,
      'type': self.type
    }