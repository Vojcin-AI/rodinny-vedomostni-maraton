import unittest
from unittest.mock import patch

import quiz_backend


class QuizFlowTest(unittest.TestCase):
    def setUp(self):
        self.data = quiz_backend.quiz_data
        self.data.teams = {}
        self.data.team_access_codes = {}
        self.data.current_question = None
        self.data.current_question_started_at = None
        self.data.question_index = 0
        self.data.quiz_state = 'waiting'
        self.client = quiz_backend.app.test_client()
        response = self.client.post(
            '/api/admin/login',
            json={'password': self.data.admin_password},
        )
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.data.teams = {}
        self.data.team_access_codes = {}
        self.data.current_question = None
        self.data.current_question_started_at = None
        self.data.question_index = 0
        self.data.quiz_state = 'waiting'

    def register_team(self, name):
        response = self.client.post('/api/team/register', json={'team_name': name})
        self.assertEqual(response.status_code, 200)
        return response.get_json()['team_id']

    def test_next_question_waits_for_every_team(self):
        first_team = self.register_team('První tým')
        second_team = self.register_team('Druhý tým')
        self.assertEqual(self.client.post('/api/admin/start-quiz').status_code, 200)
        first_question = self.client.post('/api/admin/next-question')
        self.assertEqual(first_question.status_code, 200)
        question_id = first_question.get_json()['question']['id']

        blocked = self.client.post('/api/admin/next-question')
        self.assertEqual(blocked.status_code, 409)

        activity = self.client.post(
            '/api/team/activity',
            json={'team_id': first_team, 'question_id': question_id},
        )
        self.assertEqual(activity.status_code, 200)
        status = self.client.get('/api/admin/leaderboard').get_json()
        team_status = {
            team['team_id']: team['answer_status']
            for team in status['leaderboard']
        }
        self.assertEqual(team_status[first_team], 'typing')
        self.assertEqual(team_status[second_team], 'waiting')

        for team_id in (first_team, second_team):
            response = self.client.post(
                '/api/team/submit-answer',
                json={
                    'team_id': team_id,
                    'question_id': question_id,
                    'answer': 'Matěj',
                },
            )
            self.assertEqual(response.status_code, 200)

        status = self.client.get('/api/admin/leaderboard').get_json()
        self.assertTrue(status['all_answered'])
        self.assertEqual(status['answered_count'], 2)

        next_question = self.client.post('/api/admin/next-question')
        self.assertEqual(next_question.status_code, 200)
        self.assertEqual(next_question.get_json()['question']['id'], 2)

    def test_admin_created_team_can_log_in_using_code(self):
        response = self.client.post(
            '/api/admin/teams',
            json={'team_name': 'Předem připravený tým'},
        )
        self.assertEqual(response.status_code, 200)
        credentials = response.get_json()

        login = self.client.post(
            '/api/team/login',
            json={'login_code': credentials['login_code'].lower()},
        )
        self.assertEqual(login.status_code, 200)
        self.assertEqual(login.get_json()['team_id'], credentials['team_id'])
        self.assertEqual(login.get_json()['team_name'], 'Předem připravený tým')
        self.assertEqual(len(self.data.teams), 1)
        public_board = quiz_backend.app.test_client().get('/api/leaderboard')
        self.assertEqual(public_board.status_code, 200)
        public_team = public_board.get_json()['leaderboard'][0]
        self.assertNotIn('login_code', public_team)

    def test_response_time_is_accumulated_but_does_not_change_ranking(self):
        first_team = self.register_team('Rychlý')
        second_team = self.register_team('Pomalejší')
        self.client.post('/api/admin/start-quiz')
        with patch('quiz_backend.time.monotonic', return_value=100.0):
            question = self.client.post('/api/admin/next-question').get_json()['question']

        with patch('quiz_backend.time.monotonic', return_value=105.0):
            first_answer = self.client.post(
                '/api/team/submit-answer',
                json={
                    'team_id': first_team,
                    'question_id': question['id'],
                    'answer': 'Matěj',
                },
            )
        with patch('quiz_backend.time.monotonic', return_value=102.5):
            second_answer = self.client.post(
                '/api/team/submit-answer',
                json={
                    'team_id': second_team,
                    'question_id': question['id'],
                    'answer': 'Matěj',
                },
            )

        self.assertEqual(first_answer.get_json()['response_time_seconds'], 5.0)
        self.assertEqual(second_answer.get_json()['response_time_seconds'], 2.5)

        with patch('quiz_backend.time.monotonic', return_value=200.0):
            second_question = self.client.post('/api/admin/next-question').get_json()['question']
        with patch('quiz_backend.time.monotonic', return_value=206.75):
            self.client.post(
                '/api/team/submit-answer',
                json={
                    'team_id': first_team,
                    'question_id': second_question['id'],
                    'answer': 'Božena',
                },
            )
        with patch('quiz_backend.time.monotonic', return_value=201.0):
            self.client.post(
                '/api/team/submit-answer',
                json={
                    'team_id': second_team,
                    'question_id': second_question['id'],
                    'answer': 'Božena',
                },
            )

        leaderboard = self.client.get('/api/admin/leaderboard').get_json()['leaderboard']
        teams_by_id = {team['team_id']: team for team in leaderboard}
        self.assertEqual(teams_by_id[first_team]['total_response_time_seconds'], 11.75)
        self.assertEqual(teams_by_id[second_team]['total_response_time_seconds'], 3.5)
        self.assertEqual(leaderboard[0]['team_id'], first_team)

    def test_manual_team_cannot_be_added_after_quiz_starts(self):
        self.client.post('/api/admin/start-quiz')
        response = self.client.post(
            '/api/admin/teams',
            json={'team_name': 'Pozdní tým'},
        )
        self.assertEqual(response.status_code, 409)


if __name__ == '__main__':
    unittest.main()
