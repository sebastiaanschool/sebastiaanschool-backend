from datetime import timedelta
from textwrap import dedent

from django.contrib.auth import get_user_model
from django.utils import timezone
from pytz import utc
from rest_framework.test import APITestCase
from warnings import filterwarnings

from models import AgendaItem, Bulletin, ContactItem, Newsletter, UserDevice


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

        get_user_model().objects.create_user('mere-mortal', 'myemail@example.com', 'I have no power')
        get_user_model().objects.create_superuser('admin', 'myemail@example.com', 'I have the power')

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

    def test_agenda_get_agenda_items_returns_ascending_order_starting_today(self):
        """
        Ensures that when we GET agendaItems, they're in ascending order by date, and past agendaItems are not included.
        """
        response = self.client.get('/api/agendaItems/')
        response.render()
        self.assertEqual(response.content, self.expectations['coming_agenda_items'])

    def test_agenda_get_all_agenda_items_returns_ascending_order(self):
        """
        Ensures that when we GET agendaItems?all, they're in ascending order by date, and past agendaItems are included.
        """
        response = self.client.get('/api/agendaItems/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['all_agenda_items'])

    def test_agenda_post_agenda_item_unauthenticated_is_not_allowed(self):
        response = self.client.post('/api/agendaItems/', {'title': 'Access denied',
                                                          'type': 'Event',
                                                          'start': '2016-03-10T20:00:00Z',
                                                          'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_agenda_post_agenda_item_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.post('/api/agendaItems/', {'title': 'Access denied',
                                                          'type': 'Event',
                                                          'start': '2016-03-10T20:00:00Z',
                                                          'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_agenda_post_agenda_item_as_admin_is_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.post('/api/agendaItems/', {'title': 'Access granted',
                                                          'type': 'Event',
                                                          'start': '2016-03-10T20:00:00Z',
                                                          'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(AgendaItem.objects.count(), 4)

    def test_agenda_put_agenda_item_unauthenticated_is_not_allowed(self):
        response = self.client.put('/api/agendaItems/', {'title': 'Access denied',
                                                         'type': 'Event',
                                                         'start': '2016-03-10T20:00:00Z',
                                                         'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_agenda_put_agenda_item_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.put('/api/agendaItems/', {'title': 'Access denied',
                                                         'type': 'Event',
                                                         'start': '2016-03-10T20:00:00Z',
                                                         'end': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_agenda_put_agenda_item_as_admin_is_not_allowed(self):
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

        get_user_model().objects.create_user('mere-mortal', 'myemail@example.com', 'I have no power')
        get_user_model().objects.create_superuser('admin', 'myemail@example.com', 'I have the power')

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

    def test_bulletin_get_bulletins_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET bulletins, they're in descending order by date, and future bulletins are not included.
        """
        response = self.client.get('/api/bulletins/')
        response.render()
        self.assertEqual(response.content, self.expectations['todays_bulletins'])

    def test_bulletin_get_all_bulletins_unauthenticated_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET bulletins?all anonymously, they're in descending order by date, and future bulletins
        are not included.
        """
        response = self.client.get('/api/bulletins/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['todays_bulletins'])

    def test_bulletin_get_all_bulletins_as_normal_user_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET bulletins?all anonymously, they're in descending order by date, and future bulletins
        are not included.
        """
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.get('/api/bulletins/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['todays_bulletins'])

    def test_bulletin_get_all_bulletins_as_admin_returns_descending_order_including_future(self):
        """
        Ensures that when we GET bulletins?all as admin, they're in descending order by date, and future bulletins are
        included.
        """
        self.client.login(username='admin', password='I have the power')
        response = self.client.get('/api/bulletins/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['all_bulletins'])

    def test_bulletin_post_bulletin_unauthenticated_is_not_allowed(self):
        response = self.client.post('/api/bulletins/', {'title': 'Access denied',
                                                        'body': 'This is not acceptable',
                                                        'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_bulletin_post_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.post('/api/bulletins/', {'title': 'Access denied',
                                                        'body': 'This is not acceptable',
                                                        'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_bulletin_post_bulletin_as_admin_is_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.post('/api/bulletins/', {'title': 'Access granted',
                                                        'body': 'This is allowed',
                                                        'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Bulletin.objects.count(), 4)

    def test_bulletin_put_bulletin_unauthenticated_is_not_allowed(self):
        response = self.client.put('/api/bulletins/', {'title': 'Access denied',
                                                       'body': 'This is not acceptable',
                                                       'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_bulletin_put_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.put('/api/bulletins/', {'title': 'Access denied',
                                                       'body': 'This is not acceptable',
                                                       'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_bulletin_put_bulletin_as_admin_is_not_allowed(self):
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

        get_user_model().objects.create_user('mere-mortal', 'myemail@example.com', 'I have no power')
        get_user_model().objects.create_superuser('admin', 'myemail@example.com', 'I have the power')

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

    def test_contact_item_get_contact_items_returns_contacts_in_field_order(self):
        """
        Ensures that when we GET contactItems, they're in ascending order by `order`.
        """
        response = self.client.get('/api/contactItems/')
        response.render()
        self.assertEqual(response.content, self.expectations['all_contacts'])

    def test_contact_item_post_contact_item_unauthenticated_is_not_allowed(self):
        response = self.client.post('/api/contactItems/', {'displayName': 'David Davidson',
                                                           'email': 'dd@example.com',
                                                           'order': 4,
                                                           'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 403)

    def test_contact_item_post_contact_item_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.post('/api/contactItems/', {'displayName': 'David Davidson',
                                                           'email': 'dd@example.com',
                                                           'order': 4,
                                                           'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 403)

    def test_contact_item_post_contact_item_as_admin_is_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.post('/api/contactItems/', {'displayName': 'David Davidson',
                                                           'email': 'dd@example.com',
                                                           'order': 4,
                                                           'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(ContactItem.objects.count(), 4)

    def test_contact_item_put_contact_item_unauthenticated_is_not_allowed(self):
        response = self.client.put('/api/contactItems/', {'displayName': 'David Davidson',
                                                          'email': 'dd@example.com',
                                                          'order': 4,
                                                          'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 403)

    def test_contact_item_put_contact_item_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.put('/api/contactItems/', {'displayName': 'David Davidson',
                                                          'email': 'dd@example.com',
                                                          'order': 4,
                                                          'detailText': 'David doesn\'t dance daily.'})
        self.assertEqual(response.status_code, 403)

    def test_contact_item_put_contact_item_as_admin_is_not_allowed(self):
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

        get_user_model().objects.create_user('mere-mortal', 'myemail@example.com', 'I have no power')
        get_user_model().objects.create_superuser('admin', 'myemail@example.com', 'I have the power')

        cls.expectations = dict(
            all_newsletters=dedent("""
                [{"title":"Next month\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsletters/3/"},
                {"title":"Today\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsletters/1/"},
                {"title":"Last month\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsletters/2/"}]""")
                .replace('\n', '')
                % (cls.next_month_str, cls.today_str, cls.last_month_str),
            todays_newsletters=dedent("""
                [{"title":"Today\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsletters/1/"},
                {"title":"Last month\'s news","documentUrl":"https://github.com/sebastiaanschool"
                ,"publishedAt":"%s","url":"http://testserver/api/newsletters/2/"}]""")
                .replace('\n', '')
                % (cls.today_str, cls.last_month_str)
        )

    def test_newsletter_get_newsletters_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET newsletters, they're in descending order by date, and future ones are not included.
        """
        response = self.client.get('/api/newsletters/')
        response.render()
        self.assertEqual(response.content, self.expectations['todays_newsletters'])

    def test_newsletter_get_all_newsletters_unauthenticated_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET newsletters?all anonymously, they're in descending order by date, and future ones
        are not included.
        """
        response = self.client.get('/api/newsletters/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['todays_newsletters'])

    def test_newsletter_get_all_newsletters_as_normal_user_returns_descending_order_up_to_today(self):
        """
        Ensures that when we GET newsletters?all anonymously, they're in descending order by date, and future ones
        are not included.
        """
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.get('/api/newsletters/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['todays_newsletters'])

    def test_newsletter_get_all_newsletters_as_admin_returns_descending_order_including_future(self):
        """
        Ensures that when we GET newsletters?all as admin, they're in descending order by date, and future ones are
        included.
        """
        self.client.login(username='admin', password='I have the power')
        response = self.client.get('/api/newsletters/', {'all': ''})
        response.render()
        self.assertEqual(response.content, self.expectations['all_newsletters'])

    def test_newsletter_post_bulletin_unauthenticated_is_not_allowed(self):
        response = self.client.post('/api/newsletters/', {'title': 'Access denied',
                                                          'documentUrl': 'This is not acceptable',
                                                          'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_newsletter_post_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.post('/api/newsletters/', {'title': 'Access denied',
                                                          'documentUrl': 'This is not acceptable',
                                                          'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_newsletter_post_bulletin_as_admin_is_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.post('/api/newsletters/', {'title': 'Access granted',
                                                          'documentUrl': 'This is allowed',
                                                          'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Newsletter.objects.count(), 4)

    def test_newsletter_put_bulletin_unauthenticated_is_not_allowed(self):
        response = self.client.put('/api/newsletters/', {'title': 'Access denied',
                                                         'documentUrl': 'This is not acceptable',
                                                         'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_newsletter_put_bulletin_as_normal_user_is_not_allowed(self):
        self.client.login(username='mere-mortal', password='I have no power')
        response = self.client.put('/api/newsletters/', {'title': 'Access denied',
                                                         'documentUrl': 'This is not acceptable',
                                                         'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 403)

    def test_newsletter_put_bulletin_as_admin_is_not_allowed(self):
        self.client.login(username='admin', password='I have the power')
        response = self.client.put('/api/newsletters/', {'title': 'Access denied',
                                                         'documentUrl': 'This is not acceptable',
                                                         'publishedAt': '2016-03-10T20:00:00Z'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Newsletter.objects.count(), 3)


class UserDeviceTests(APITestCase):

    @classmethod
    def setUpTestData(cls):
        user1 = get_user_model().objects.create_user('one', None, 'password1')
        user2 = get_user_model().objects.create_user('two', None, 'password2')
        UserDevice.objects.create(user=user1,
                                  wants_push_notifications=True,
                                  firebase_instance_id='iid1')
        UserDevice.objects.create(user=user2,
                                  wants_push_notifications=False)

    def test_user_device_can_enroll_anonymously(self):
        """
        Ensures that we can enroll (create a user anonymously), we get (201 created).
        """
        response = self.client.post('/api/enrollment',
                                    {'username':'22222222-4321-1234-abcd-4321abcd1234',
                                     'password':'bbbbbbbb-4321-abcd-1234-4321abcd1234'})
        self.assertEqual(response.status_code, 204)
        user = get_user_model().objects.get(username="22222222-4321-1234-abcd-4321abcd1234")
        self.assertIsNotNone(user)
        push_prefs = UserDevice.objects.get(user=user)
        self.assertIsNotNone(push_prefs)
        self.assertFalse(push_prefs.wants_push_notifications)
        self.assertIsNone(push_prefs.firebase_instance_id)
        self.assertTrue(self.client.login(
            username='22222222-4321-1234-abcd-4321abcd1234',
            password='bbbbbbbb-4321-abcd-1234-4321abcd1234'))

    def test_user_device_cannot_enroll_when_already_logged_in(self):
        """
        Ensures that we cannot enroll when we are already logged in (400 bad request).
        """
        self.client.login(username='one', password='password1')
        response = self.client.post('/api/enrollment',
                                    {'username':'11111111-4321-1234-abcd-4321abcd1234',
                                     'password':'aaaaaaaa-4321-abcd-1234-4321abcd1234'})
        self.assertEqual(response.status_code, 400)

    def test_user_device_cannot_GET_user_device_anonymously(self):
        """
        Ensures that when we GET /api/push-settings anonymously, we get (401 unauthorized).
        """
        response = self.client.get('/api/push-settings')
        self.assertEqual(response.status_code, 403)

    def test_user_device_cannot_PUT_user_device_anonymously(self):
        """
        Ensures that when we PUT /api/push-settings anonymously, we get (401 unauthorized).
        """
        response = self.client.put('/api/push-settings',
                                   {'notify_me': True,
                                    'firebase_iid': 'iid-test'})
        self.assertEqual(response.status_code, 403)

    def test_user_device_cannot_POST_user_device_anonymously(self):
        """
        Ensures that when we DELETE /api/push-settings anonymously, we get (401 unauthorized).
        """
        response = self.client.post('/api/push-settings',
                                   {'notify_me': True,
                                    'firebase_iid': 'iid-test'})
        self.assertEqual(response.status_code, 403)

    def test_user_device_cannot_DELETE_user_device_anonymously(self):
        """
        Ensures that when we DELETE /api/push-settings anonymously, we get (401 unauthorized).
        """
        response = self.client.delete('/api/push-settings')
        self.assertEqual(response.status_code, 403)

    def test_user_device_normal_user_can_GET_self(self):
        """
        Ensures that when we GET /api/push-settings while logged in, we get (200 ok + our data).
        """
        self.client.login(username='one', password='password1')
        response = self.client.get('/api/push-settings')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"notify_me":true}')

    def test_user_device_normal_user_cannot_PUT_self(self):
        """
        Ensures that when we PUT /api/push-settings while logged in, we get (405 method not allowed).
        """
        self.client.login(username='one', password='password1')
        response = self.client.put('/api/push-settings', {'notify_me': False})
        self.assertEqual(response.status_code, 405)

    def test_user_device_normal_user_cannot_DELETE_self(self):
        """
        Ensures that when we PUT /api/push-settings while logged in, we get (405 method not allowed).
        """
        self.client.login(username='one', password='password1')
        response = self.client.delete('/api/push-settings')
        self.assertEqual(response.status_code, 405)

    def test_user_device_normal_user_can_POST_self_to_clear_data(self):
        """
        Ensures that when we POST /api/push-settings while logged in, we get (200 and content).
        """
        self.client.login(username='one', password='password1')
        response = self.client.post('/api/push-settings', data='{"notify_me": false}', content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"notify_me":false}')
        user = get_user_model().objects.get(username="one")
        user_device = UserDevice.objects.get(user=user)
        self.assertFalse(user_device.wants_push_notifications)
        self.assertIsNone(user_device.firebase_instance_id)

    def test_user_device_normal_user_can_POST_self_to_clear_data_ignoring_iid(self):
        """
        Ensures that when we POST /api/push-settings while logged in, we get (200 and content).
        Ensures that a firebase_iid included in the request is cleared
        """
        self.client.login(username='one', password='password1')
        response = self.client.post('/api/push-settings', data='{"notify_me": false, "firebase_iid": "1234-5678-abcdefgh"}', content_type="application/json")
        self.assertEqual(response.status_code, 200)
        user = get_user_model().objects.get(username="one")
        user_device = UserDevice.objects.get(user=user)
        self.assertIsNone(user_device.firebase_instance_id)

    def test_user_device_normal_user_can_POST_self_to_set_data(self):
        """
        Ensures that when we POST /api/push-settings while logged in, we get (204 no content).
        """
        self.client.login(username='one', password='password1')
        response = self.client.post('/api/push-settings', '{"notify_me": true, "firebase_iid": "1234-5678-abcdefgh"}', content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, '{"notify_me":true}')
        user = get_user_model().objects.get(username="one")
        user_device = UserDevice.objects.get(user=user)
        self.assertTrue(user_device.wants_push_notifications)
        self.assertEqual(user_device.firebase_instance_id, '1234-5678-abcdefgh')

    def test_user_device_POST_bad_input_1(self):
        """
        Ensures that when we POST /api/push-settings while logged in, we handle bad input reasonably.
        """
        self.client.login(username='one', password='password1')
        response = self.client.post('/api/push-settings', '{"notify_me": "always", "firebase_iid": "1234-5678-abcdefgh"}', content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"reason":"notify_me should be true or false"}')

    def test_user_device_POST_bad_input_2(self):
        """
        Ensures that when we POST /api/push-settings while logged in, we handle bad input reasonably.
        """
        self.client.login(username='one', password='password1')
        response = self.client.post('/api/push-settings', '{"notify_me": true, "firebase_iid": "1234"}', content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"reason":"firebase_iid should be >16 and <=256"}')

    def test_user_device_POST_bad_input_3(self):
        """
        Ensures that when we POST /api/push-settings while logged in, we handle bad input reasonably.
        """
        self.client.login(username='one', password='password1')
        long_key = "".join(['a' for x in range(257)])
        response = self.client.post('/api/push-settings', '{"notify_me": true, "firebase_iid": "%s"}' % (long_key,), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"reason":"firebase_iid should be >16 and <=256"}')

    def test_user_device_POST_bad_input_4(self):
        """
        Ensures that when we POST /api/push-settings while logged in, we handle bad input reasonably.
        """
        self.client.login(username='one', password='password1')
        response = self.client.post('/api/push-settings', '{"notify_me": true, "firebase_iid": null}', content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"reason":"firebase_iid should be >16 and <=256"}')

    def test_user_device_POST_bad_input_5(self):
        """
        Ensures that when we POST /api/push-settings while logged in, we handle bad input reasonably.
        """
        self.client.login(username='one', password='password1')
        response = self.client.post('/api/push-settings', '{"notify_me": true}', content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content, '{"reason":"firebase_iid is required if notify_me is true"}')


# Make us get stack traces instead of just warnings for "naive datetime".
filterwarnings(
        'error', r"DateTimeField .* received a naive datetime",
        RuntimeWarning, r'django\.db\.models\.fields')
