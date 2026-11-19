import unittest
from app import app
from database import init_db

class TowTruckTestCase(unittest.TestCase):
    def setUp(self):
        init_db()
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()

    def test_homepage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('YOLDA MI KALDINIZ'.encode('utf-8'), response.data)
        self.assertIn('Emir Arpacı'.encode('utf-8'), response.data)

    def test_gallery_page(self):
        response = self.client.get('/gallery')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Kurtarma'.encode('utf-8'), response.data)

    def test_login_page(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('Giriş'.encode('utf-8'), response.data)

    def test_admin_login(self):
        response = self.client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Yönetici Kontrol Merkezi'.encode('utf-8'), response.data)

    def test_member_login(self):
        response = self.client.post('/login', data={
            'username': 'uye',
            'password': '123456'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Müşteri Hesabı'.encode('utf-8'), response.data)

if __name__ == '__main__':
    unittest.main()
