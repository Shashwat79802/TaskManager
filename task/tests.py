from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Task

User = get_user_model()

class TaskAPITestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', password='pass123')
        self.user2 = User.objects.create_user(username='bob', password='pass123')
        self.t1 = Task.objects.create(title='T1', description='desc1', completed=False, owner=self.user)
        self.t2 = Task.objects.create(title='T2', description='desc2', completed=True, owner=self.user2)
        print("\n\nSetup complete")

    def get_token(self, username='alice', password='pass123'):
        url = reverse('token_obtain_pair')
        resp = self.client.post(url, {'username': username, 'password': password}, format='json')
        print("\n\nToken response:", resp.data)
        return resp.data.get('access')

    def test_list_tasks_public(self):
        url = reverse('task-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data['results']), 2)
        print("\n\nList tasks response:", resp.data)

    def test_create_task_requires_auth(self):
        url = reverse('task-list')
        resp = self.client.post(url, {'title': 'New', 'description': 'd'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)
        token = self.get_token()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.post(url, {'title': 'New', 'description': 'd'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.data['owner']['username'], 'alice')
        print("\n\nCreate task response:", resp.data)

    def test_update_only_owner(self):
        url = reverse('task-detail', args=[self.t1.id])
        token = self.get_token('bob', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.put(url, {'title': 'Hacked','description':'x','completed':True}, format='json')
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        token_owner = self.get_token('alice', 'pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_owner}')
        resp = self.client.patch(url, {'completed': True}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.t1.refresh_from_db()
        self.assertTrue(self.t1.completed)
        print("\n\nUpdate task response:", resp.data)

    def test_delete_owner_or_admin(self):
        url = reverse('task-detail', args=[self.t2.id])
        token = self.get_token('alice','pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        resp = self.client.delete(url)
        self.assertIn(resp.status_code, (status.HTTP_403_FORBIDDEN, status.HTTP_404_NOT_FOUND))
        token_owner = self.get_token('bob','pass123')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_owner}')
        resp = self.client.delete(url)
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        print("\n\nDelete task response: No Content")

    def test_filter_by_completed(self):
        url = reverse('task-list') + '?completed=true'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        for item in resp.data['results']:
            self.assertTrue(item['completed'])
        print("\n\nFilter by completed response:", resp.data)
