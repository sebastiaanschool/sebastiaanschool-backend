from datetime import timedelta

from django.contrib.auth.models import User
from django.utils import timezone
from pytz import utc
from rest_framework.test import APITestCase

from models import Bulletin


class BulletinTests(APITestCase):
    """
    To run tests: execute `python manage.py test` on the command line.
    """

    @classmethod
    def setUpTestData(cls):
        today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        next_month = today + timedelta(days=31)
        last_month = today - timedelta(days=31)
        Bulletin.objects.create(
                title="Today's news",
                body="Today is the day",
                publishedAt=today)
        Bulletin.objects.create(
                title="Last month's news",
                body="Then was the day",
                publishedAt=last_month)
        Bulletin.objects.create(
                title="Next month's news",
                body="Then will be the day",
                publishedAt=next_month)

        User.objects.create_user('mere-mortal', 'myemail@example.com', 'I have no power')
        User.objects.create_superuser('admin', 'myemail@example.com', 'I have the power')

        today_str = today.astimezone(utc).strftime('%Y-%m-%dT00:00:00Z')
        next_month_str = next_month.astimezone(utc).strftime('%Y-%m-%dT00:00:00Z')
        last_month_str = last_month.astimezone(utc).strftime('%Y-%m-%dT00:00:00Z')

        cls.expectations = dict(
            all_bulletins='[{"title":"Next month\'s news","body":"Then will be the day","publishedAt":"' + next_month_str + '"},{"title":"Today\'s news","body":"Today is the day","publishedAt":"' + today_str + '"},{"title":"Last month\'s news","body":"Then was the day","publishedAt":"' + last_month_str + '"}]',
            todays_bulletins = '[{"title":"Today\'s news","body":"Today is the day","publishedAt":"' + today_str + '"},{"title":"Last month\'s news","body":"Then was the day","publishedAt":"' + last_month_str + '"}]'
        )

    def test_get_bulletins_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET bulletins, they're in descending order by date, and future bulletins are not included.
        """
        response = self.client.get('/api/bulletins/')
        response.render()
        self.assertEqual(response.content, self.expectations['todays_bulletins'])

    def test_get_all_bulletins_unauthenticated_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET bulletins?all anonymously, they're in descending order by date, and future bulletins
        are not included.
        """
        response = self.client.get('/api/bulletins/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['todays_bulletins'])

    def test_get_all_bulletins_as_normal_user_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET bulletins?all anonymously, they're in descending order by date, and future bulletins
        are not included.
        """
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.get('/api/bulletins/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['todays_bulletins'])

    def test_get_all_bulletins_as_admin_returns_descending_order_including_future(self):
        """
        Ensures that when we GET bulletins?all as admin, they're in descending order by date, and future bulletins are
        included.
        """
        self.client.login(username='admin', password='I have the power')
        response = self.client.get('/api/bulletins/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['all_bulletins'])

    def test_post_bulletin_unauthenticated_is_not_allowed(self):
        response = self.client.post('/api/bulletins/', {'title':'Access denied', 'body':'This is not acceptable', 'publishedAt':'2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_post_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.post('/api/bulletins/', {'title':'Access denied', 'body':'This is not acceptable', 'publishedAt':'2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_post_bulletin_as_admin_is_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.post('/api/bulletins/', {'title':'Access granted', 'body':'This is allowed', 'publishedAt':'2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Bulletin.objects.count(), 4)

    def test_put_bulletin_unauthenticated_is_not_allowed(self):
        response = self.client.put('/api/bulletins/', {'title':'Access denied', 'body':'This is not acceptable', 'publishedAt':'2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_put_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.put('/api/bulletins/', {'title':'Access denied', 'body':'This is not acceptable', 'publishedAt':'2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_put_bulletin_as_admin_is_not_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.put('/api/bulletins/', {'title':'Access denied', 'body':'This is not acceptable', 'publishedAt':'2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Bulletin.objects.count(), 3)
