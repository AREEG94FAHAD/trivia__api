import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from  sqlalchemy.sql.expression import func, select
from flask_cors import CORS
import random

from models import setup_db, Question, Category

#use for specify number of questions should apear per page
QUESTIONS_PER_PAGE = 10

#functions use to select specific questions per page
#127.0.0.1/questions/page=2 will retrive only next page first ten questions will not appera
#if you type page=3 will show questions from 21 to 30 and so on.
def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start =  (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE
  #format is function in model will arrange data like in it
  questions = [question.format() for question in selection]
  #select data from page =1 to 10
  current_questions = questions[start:end]
  return current_questions

#in flaskr all code of your web page must type in this function and name must it create_app
def create_app(test_config=None):

  # create and configure the app
  app = Flask(__name__)
  #setup your app base on models 
  setup_db(app)
  
  # used cors to managment access to your link in this case we create api 
  # of caegories each cateogery have set of questions
  #can access y any one
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  #this use to specify methods that used to api get,patch post and so one to managment my api
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
      response.headers.add('Access-Control-Allow-Methods', 'GET,PATCH,POST,DELETE,OPTIONS')
      return response

#simple route this use just to return all categories of your api 
  @app.route('/categories')
  def get_categories():
#select all cateogeries
    categories = Category.query.all()
    #if not have categoreies will return 404 error handler
    if len(categories) == 0:
      abort(404)
#convet cateogeries in to jsonify like [x for i in range(4)] same way but in this case with objects

    categ = {cat.id:cat.type for cat in categories}
    return jsonify({
      'success':True,
      'categories':categ
    })

# route to return all questions in your database
  @app.route('/questions')
  def get_questions():
   
    questions = Question.query.all()

    if questions is None:
      abort(404)
#only allow ten quesions in each page so function paginate used here
    current_questions = paginate_questions(request, questions)

    categories = Category.query.all()

    categ = {cat.id:cat.type for cat in categories}

    return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(questions),
            'categories': categ
        })
# route for handel delete request by id of questions
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    
    try:
      #take question id and serach for it in database of question
      retrive_question = Question.query.filter(Question.id == question_id).one()
      #if the question not found this will return 404 error
      if retrive_question is None:
        abort(404)
      retrive_question.delete()
      return jsonify({
        'success':True,
        'question_id_deleted': question_id
      })

      #if your system not remove your question say 422 error 
    except:
      abort(422)


#route to do two things first added new question or search for specify questions 
  @app.route('/questions', methods=['POST'])
  def add_new_questions():
    try:
      #to get data from ajax we can use request.json.get get all properties
      searchTerm = request.json.get('searchTerm', None)
      question = request.json.get('question', None)
      answer = request.json.get('answer', None)
      difficulty = request.json.get('difficulty', None)
      category = request.json.get('category', None)

      print(searchTerm)
      # check if searchterm is not means you have data to store in database
      if searchTerm is None:
        
        #must all field have data if anyone not have data will retuen badrequest
        if ((question is None) or (answer is None ) or (difficulty is None) or (category is None)):
          abort(400)

        Question(question=question, answer=answer, difficulty=difficulty, category=category).insert()
        return jsonify({
          'success':True
        })

        #here if you looking for some questions 
      else:
        # questions = Question.query.filter(Question.question.ilike('%'+searchTerm+'%')).all()
        #select all questions to retrive
        selection = Question.query.filter(Question.question.ilike('%'+searchTerm+'%')).all()
        #used method to return only 10 questions per page
        current_questions = paginate_questions(request, selection)
        #if not receive questions you will return 404 error
        if current_questions is None:
          abort(404)

        return jsonify({
        'success': True,
        'questions': current_questions,
        'total_questions': len(selection),
        })
    except:
      abort(422)
#route to display only questions questions of specific category
  @app.route('/categories/<int:category_id>/questions')
  #take id of category
  def get_all_question_base_on_cate(category_id):

    #select all question of category 
    try:
      cate_name = Category.query.filter(Category.id == category_id).one()
      #if dont have category with specific id will return error 404
      if cate_name is None:
        abort(404)
      questions = Question.query.filter(Question.category == str(category_id)).all()
      current_questions = paginate_questions(request, questions)
      
      return jsonify({
          'success': True,
          'questions': current_questions,
          'total_questions': len(questions),
          'categories': cate_name.type
      })
    except:
      abort(422)


#####################################################################
# display quizzes base of receive previous_questions & quiz_category#
#####################################################################

  #route for play quizzes by post 
  @app.route('/quizzes', methods=['POST'])
  def quiz_base_on_catogry():

      #request.json.get to get previous-questions and get selected category 
      previous_questions = request.json.get('previous_questions', None)
      quiz_category = request.json.get('quiz_category', None)

      #get id of category and then check if you hava quetion about this category or not if not return 404
      try:
          category = quiz_category.get('id')
          prevques = []

          #save id of all pervious question to dot show it again in next time
          for question in previous_questions:
              prevques.append(question)

          if category == 0:
            # using sheet of udacity to dont display question again by using ~ 
            next_question = Question.query.filter(~Question.id.in_(prevques)).order_by(func.random()).first()
            if next_question is None:
              return jsonify({
                'success':True
              })
          else:
            #select random question from database by this can access to this methods using link
            #https://stackoverflow.com/questions/60805/getting-random-row-through-sqlalchemy
            next_question = Question.query.filter(Question.category==quiz_category.get('id')).filter(~Question.id.in_(prevques)).order_by(func.random()).first()
          
          if not next_question:

            return jsonify({
              'success':True
            })
          else:
              return jsonify({
                  'success': True,
                  'question': next_question.format()
              })
      except:
        abort(422)


###############################################################################
# error handler 404 for not found 422 for error processing 400 for bad request#
###############################################################################

# here is error handler if yor data empty
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success':False,
      'error':404,
      'message':' Resource Not Found'
    }),404

# ERORR HANDLER FOR TASK CAN NOT BE ACHIVE 
  @app.errorhandler(422)
  def not_Processable(error):
    return jsonify({
      'success':False,
      'error':422,
      'message':'Not Processable'
    }),422
  

  #ERROR HANDLER FOR BAD REQUES 
  @app.errorhandler(400)
  def lbad_request(error):
    return jsonify({
      'success':False,
      'error':400,
      'message':' Bad Request'
    }),400
  
  return app

    