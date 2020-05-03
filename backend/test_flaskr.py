import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

# class for unit tesst
class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""
    # funtion for setup our database

    def setUp(self):
        """Define test variables and initialize app."""

        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}:{}@{}/{}".format(
            'postgres', 'soso', 'localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

        # new question for test
        self.new_questions = {
            'question': 'Anansi Boys',
            'answer': 'Neil Gaiman',
            'category': 1,
            'difficulty': 3
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    # use for test all category if return 200 and so on
    def test_get_all_category(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    # used to test all question

    def test_get_paginated_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['categories']), 6)

    # test if deleted question successfull or not
    def test_delete_question(self):
        res = self.client().delete('/questions/15')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question_id_deleted'])

    # test if problem accour when delete quesion

    def test_4040_delete_question(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
    # test if can add new question or not

    def test_create_new_question(self):
        res = self.client().post('/questions', json=self.new_questions)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        

    # test if can search  for question
    def test_search_question(self):
        res = self.client().post('/questions', json={'searchTerm': 'a'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["total_questions"])

    # test search if dont have any data
    def test_serach_not_found(self):
        res = self.client().post('/questions', json={'searchTerm': 'kkk'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)

    # test for questions of spesific category
    def test_getQuestionsOfCategory(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['questions'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(data['categories'])

    # test unspsific category
    def test_404_getQuestionsOfCategory(self):
        res = self.client().get('/categories/12222/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)

    # #test fot
    def test_quizz(self):
        quizzes = {'previous_questions': [],
                   'quiz_category': {'type': 'Entertainment', 'id': 5}}

        res = self.client().post('/quizzes', json=quizzes)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_404_quizz(self):
        quizzes = {'previous_questions': []}

        res = self.client().post('/quizzes', json=quizzes)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)



if __name__ == "__main__":
    unittest.main()
