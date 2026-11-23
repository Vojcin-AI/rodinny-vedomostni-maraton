import unittest

import quiz_backend


class QuizFlowTest(unittest.TestCase):
    def setUp(self):
        self.data = quiz_backend.quiz_data
        self.data.teams = {}
        self.data.current_question = None
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
        self.data.current_question = None
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


if __name__ == '__main__':
    unittest.main()
