from datetime import timedelta
from textwrap import dedent

from django.contrib.auth.models import User
from django.utils import timezone
from pytz import utc
from rest_framework.test import APITestCase
from warnings import filterwarnings

from models import AgendaItem, Bulletin, ContactItem, Newsletter


# To run tests: execute `python manage.py test` on the command line.


class Base(APITestCase):
    today = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    next_month = today + timedelta(days=31)
    last_month = today - timedelta(days=31)
    today_str = today.astimezone(utc).strftime('%Y-%m-%dT00:00:00Z')
    next_month_str = next_month.astimezone(utc).strftime('%Y-%m-%dT00:00:00Z')
    last_month_str = last_month.astimezone(utc).strftime('%Y-%m-%dT00:00:00Z')


class AgendaItemTests(Base):

    @classmethod
    def setUpTestData(cls):
        next_month_end = cls.next_month + timedelta(days=31)
        next_month_end_str = next_month_end.astimezone(utc).strftime('%Y-%m-%dT00:00:00Z')
        AgendaItem.objects.create(
                title="This Month",
                type="Event",
                start=cls.today,
                end=cls.next_month)
        AgendaItem.objects.create(
                title="Last Month",
                type="Event",
                start=cls.last_month,
                end=cls.today)
        AgendaItem.objects.create(
                title="Next Month",
                type="Event",
                start=cls.next_month,
                end=next_month_end)

        User.objects.create_user('mere-mortal', 'myemail@example.com', 'I have no power')
        User.objects.create_superuser('admin', 'myemail@example.com', 'I have the power')

        cls.expectations = dict(
            all_agenda_items=dedent("""
                [{"title":"Next Month","type":"Event","start":"%s","end":"%s"
                ,"url":"http://testserver/api/agendaItems/3/"},
                {"title":"This Month","type":"Event","start":"%s","end":"%s"
                ,"url":"http://testserver/api/agendaItems/1/"},
                {"title":"Last Month","type":"Event","start":"%s","end":"%s"
                ,"url":"http://testserver/api/agendaItems/2/"}]""").replace('\n', '')
                % (cls.next_month_str, next_month_end_str,
                   cls.today_str, cls.next_month_str,
                   cls.last_month_str, cls.today_str),
            coming_agenda_items=dedent("""
                [{"title":"Next Month","type":"Event","start":"%s","end":"%s"
                ,"url":"http://testserver/api/agendaItems/3/"},
                {"title":"This Month","type":"Event","start":"%s","end":"%s"
                ,"url":"http://testserver/api/agendaItems/1/"}]""").replace('\n', '')
                % (cls.next_month_str, next_month_end_str,
                   cls.today_str, cls.next_month_str)
        )

    def test_get_agenda_items_returns_ascending_order_starting_today(self):
        """
        Ensures that when we GET agendaItems, they're in ascending order by date, and past agendaItems are not included.
        """
        response = self.client.get('/api/agendaItems/')
        response.render()
        self.assertEqual(response.content, self.expectations['coming_agenda_items'])

    def test_get_all_agenda_items_returns_ascending_order(self):
        """
        Ensures that when we GET agendaItems?all, they're in ascending order by date, and past agendaItems are included.
        """
        response = self.client.get('/api/agendaItems/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['all_agenda_items'])

    def test_post_agenda_item_unauthenticated_is_not_allowed(self):
        response = self.client.post('/api/agendaItems/', {'title': 'Access denied',
                                                          'type': 'Event',
                                                          'start': '2016-03-10T20:00:00Z',
                                                          'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_post_agenda_item_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.post('/api/agendaItems/', {'title': 'Access denied',
                                                          'type': 'Event',
                                                          'start': '2016-03-10T20:00:00Z',
                                                          'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_post_agenda_item_as_admin_is_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.post('/api/agendaItems/', {'title': 'Access granted',
                                                          'type': 'Event',
                                                          'start': '2016-03-10T20:00:00Z',
                                                          'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(AgendaItem.objects.count(), 4)

    def test_put_agenda_item_unauthenticated_is_not_allowed(self):
        response = self.client.put('/api/agendaItems/', {'title': 'Access denied',
                                                         'type': 'Event',
                                                         'start': '2016-03-10T20:00:00Z',
                                                         'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_put_agenda_item_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.put('/api/agendaItems/', {'title': 'Access denied',
                                                         'type': 'Event',
                                                         'start': '2016-03-10T20:00:00Z',
                                                         'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_put_agenda_item_as_admin_is_not_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.put('/api/agendaItems/', {'title': 'Access denied',
                                                         'type': 'Event',
                                                         'start': '2016-03-10T20:00:00Z',
                                                         'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(AgendaItem.objects.count(), 3)


class BulletinTests(Base):

    @classmethod
    def setUpTestData(cls):
        Bulletin.objects.create(
                title="Today's news",
                body="Today is the day",
                publishedAt=cls.today)
        Bulletin.objects.create(
                title="Last month's news",
                body="Then was the day",
                publishedAt=cls.last_month)
        Bulletin.objects.create(
                title="Next month's news",
                body="Then will be the day",
                publishedAt=cls.next_month)

        User.objects.create_user('mere-mortal', 'myemail@example.com', 'I have no power')
        User.objects.create_superuser('admin', 'myemail@example.com', 'I have the power')

        cls.expectations = dict(
            all_bulletins=dedent("""
                [{"title":"Next month\'s news","body":"Then will be the day"
                ,"publishedAt":"%s","url":"http://testserver/api/bulletins/3/"},
                {"title":"Today\'s news","body":"Today is the day"
                ,"publishedAt":"%s","url":"http://testserver/api/bulletins/1/"},
                {"title":"Last month\'s news","body":"Then was the day"
                ,"publishedAt":"%s","url":"http://testserver/api/bulletins/2/"}]""").replace('\n', '')
                % (cls.next_month_str, cls.today_str, cls.last_month_str),
            todays_bulletins=dedent("""
                [{"title":"Today\'s news","body":"Today is the day"
                ,"publishedAt":"%s","url":"http://testserver/api/bulletins/1/"},
                {"title":"Last month\'s news","body":"Then was the day"
                ,"publishedAt":"%s","url":"http://testserver/api/bulletins/2/"}]""").replace('\n', '')
                % (cls.today_str, cls.last_month_str)
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
        response = self.client.post('/api/bulletins/', {'title': 'Access denied',
                                                        'body': 'This is not acceptable',
                                                        'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_post_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.post('/api/bulletins/', {'title': 'Access denied',
                                                        'body': 'This is not acceptable',
                                                        'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_post_bulletin_as_admin_is_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.post('/api/bulletins/', {'title': 'Access granted',
                                                        'body': 'This is allowed',
                                                        'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Bulletin.objects.count(), 4)

    def test_put_bulletin_unauthenticated_is_not_allowed(self):
        response = self.client.put('/api/bulletins/', {'title': 'Access denied',
                                                       'body': 'This is not acceptable',
                                                       'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_put_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.put('/api/bulletins/', {'title': 'Access denied',
                                                       'body': 'This is not acceptable',
                                                       'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_put_bulletin_as_admin_is_not_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.put('/api/bulletins/', {'title': 'Access denied',
                                                       'body': 'This is not acceptable',
                                                       'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Bulletin.objects.count(), 3)


class ContactItemTests(Base):

    @classmethod
    def setUpTestData(cls):
        ContactItem.objects.create(
                displayName="Connie Carlson",
                order=3,
                email="cc@example.com",
                detailText="Connie constantly causes confusion.")
        ContactItem.objects.create(
                displayName="Anna Anderson",
                order=1,
                email="aa@example.com",
                detailText="Anna always achieves awesomeness.")
        ContactItem.objects.create(
                displayName="Bernard Benson",
                order=2,
                email="bb@example.com",
                detailText="Ben brilliantly bakes biscuits.")

        User.objects.create_user('mere-mortal', 'myemail@example.com', 'I have no power')
        User.objects.create_superuser('admin', 'myemail@example.com', 'I have the power')

        cls.expectations = dict(
            all_contacts=dedent("""
                [{"displayName":"Anna Anderson",
                "email":"aa@example.com",
                "order":1,
                "detailText":"Anna always achieves awesomeness.",
                "url":"http://testserver/api/contactItems/2/"},
                {"displayName":"Bernard Benson",
                "email":"bb@example.com",
                "order":2,
                "detailText":"Ben brilliantly bakes biscuits.",
                "url":"http://testserver/api/contactItems/3/"},
                {"displayName":"Connie Carlson",
                "email":"cc@example.com",
                "order":3,
                "detailText":"Connie constantly causes confusion.",
                "url":"http://testserver/api/contactItems/1/"}]""").replace('\n', ''),
        )

    def test_get_contact_items_returns_contacts_in_field_order(self):
        """
        Ensures that when we GET contactItems, they're in ascending order by `order`.
        """
        response = self.client.get('/api/contactItems/')
        response.render()
        self.assertEqual(response.content, self.expectations['all_contacts'])

    def test_post_contact_item_unauthenticated_is_not_allowed(self):
        response = self.client.post('/api/contactItems/', {'displayName': 'David Davidson',
                                                           'email': 'dd@example.com',
                                                           'order': 4,
                                                           'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 403)

    def test_post_contact_item_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.post('/api/contactItems/', {'displayName': 'David Davidson',
                                                           'email': 'dd@example.com',
                                                           'order': 4,
                                                           'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 403)

    def test_post_contact_item_as_admin_is_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.post('/api/contactItems/', {'displayName': 'David Davidson',
                                                           'email': 'dd@example.com',
                                                           'order': 4,
                                                           'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactItem.objects.count(), 4)

    def test_put_contact_item_unauthenticated_is_not_allowed(self):
        response = self.client.put('/api/contactItems/', {'displayName': 'David Davidson',
                                                          'email': 'dd@example.com',
                                                          'order': 4,
                                                          'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 403)

    def test_put_contact_item_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.put('/api/contactItems/', {'displayName': 'David Davidson',
                                                          'email': 'dd@example.com',
                                                          'order': 4,
                                                          'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 403)

    def test_put_contact_item_as_admin_is_not_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.put('/api/contactItems/', {'displayName': 'David Davidson',
                                                          'email': 'dd@example.com',
                                                          'order': 4,
                                                          'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(ContactItem.objects.count(), 3)


class NewsletterTests(Base):

    @classmethod
    def setUpTestData(cls):
        Newsletter.objects.create(
                title="Today's news",
                documentUrl="https://github.com/sebastiaanschool",
                publishedAt=cls.today)
        Newsletter.objects.create(
                title="Last month's news",
                documentUrl="https://github.com/sebastiaanschool",
                publishedAt=cls.last_month)
        Newsletter.objects.create(
                title="Next month's news",
                documentUrl="https://github.com/sebastiaanschool",
                publishedAt=cls.next_month)

        User.objects.create_user('mere-mortal', 'myemail@example.com', 'I have no power')
        User.objects.create_superuser('admin', 'myemail@example.com', 'I have the power')

        cls.expectations = dict(
            all_newsletters=dedent("""
                [{"title":"Next month\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsLetters/3/"},
                {"title":"Today\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsLetters/1/"},
                {"title":"Last month\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsLetters/2/"}]""")
                .replace('\n', '')
                % (cls.next_month_str, cls.today_str, cls.last_month_str),
            todays_newsletters=dedent("""
                [{"title":"Today\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsLetters/1/"},
                {"title":"Last month\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsLetters/2/"}]""")
                .replace('\n', '')
                % (cls.today_str, cls.last_month_str)
        )

    def test_get_newsletters_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET newsletters, they're in descending order by date, and future ones are not included.
        """
        response = self.client.get('/api/newsLetters/')
        response.render()
        self.assertEqual(response.content, self.expectations['todays_newsletters'])

    def test_get_all_newsletters_unauthenticated_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET newsletters?all anonymously, they're in descending order by date, and future ones
        are not included.
        """
        response = self.client.get('/api/newsLetters/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['todays_newsletters'])

    def test_get_all_newsletters_as_normal_user_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET newsletters?all anonymously, they're in descending order by date, and future ones
        are not included.
        """
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.get('/api/newsLetters/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['todays_newsletters'])

    def test_get_all_newsletters_as_admin_returns_descending_order_including_future(self):
        """
        Ensures that when we GET newsletters?all as admin, they're in descending order by date, and future ones are
        included.
        """
        self.client.login(username='admin', password='I have the power')
        response = self.client.get('/api/newsLetters/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['all_newsletters'])

    def test_post_bulletin_unauthenticated_is_not_allowed(self):
        response = self.client.post('/api/newsLetters/', {'title': 'Access denied',
                                                          'documentUrl': 'This is not acceptable',
                                                          'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_post_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.post('/api/newsLetters/', {'title': 'Access denied',
                                                          'documentUrl': 'This is not acceptable',
                                                          'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_post_bulletin_as_admin_is_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.post('/api/newsLetters/', {'title': 'Access granted',
                                                          'documentUrl': 'This is allowed',
                                                          'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Newsletter.objects.count(), 4)

    def test_put_bulletin_unauthenticated_is_not_allowed(self):
        response = self.client.put('/api/newsLetters/', {'title': 'Access denied',
                                                         'documentUrl': 'This is not acceptable',
                                                         'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_put_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.put('/api/newsLetters/', {'title': 'Access denied',
                                                         'documentUrl': 'This is not acceptable',
                                                         'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_put_bulletin_as_admin_is_not_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.put('/api/newsLetters/', {'title': 'Access denied',
                                                         'documentUrl': 'This is not acceptable',
                                                         'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Newsletter.objects.count(), 3)


# Make us get stack traces instead of just warnings for "naive datetime".
filterwarnings(
        'error', r"DateTimeField .* received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')
