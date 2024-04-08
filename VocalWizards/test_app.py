import unittest
from app import app, db, Users

class TestFlaskApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use a test database
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    #Test home page
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    #Test login
    def test_login(self):
        with app.app_context():
            # Test login with correct credentials
            user = Users(username='test_user', email='test@example.com', password='password')
            db.session.add(user)
            db.session.commit()

            response = self.client.post('/login', data=dict(email='test@example.com', password='password'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'user logged successfully!', response.data)

            # Test login with incorrect credentials
            response = self.client.post('/login', data=dict(email='test@example.com', password='wrong_password'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    #Test logout
    def test_logout(self):
        with self.client.session_transaction() as sess:
            sess['username'] = 'test_user'
        response = self.client.get('/logout', follow_redirects=True)
        self.assertNotIn(b'test_user', response.data)

    def test_register(self):
        response = self.client.post('/register', data=dict(username='test_user', email='test@example.com', password='password'), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User registration completed!', response.data)

    # Test sending OTP
    def test_send_otp(self):
        response = self.client.post('/send', data=dict(
            email='test@example.com'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        

    # Test accessing protected pages without login
    def test_protected_page_access(self):
        # Attempt to access a protected page without login
        response = self.client.get('/equalizer', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login required to use the functionality!', response.data)

    # Test accessing contact page without login
    def test_contact_page_access(self):
        response = self.client.get('/contact', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please login to use this functionality', response.data)

    # Test registering with missing fields
    def test_register_missing_fields(self):
        response = self.client.post('/register', data=dict(
            username='',
            email='',
            password=''
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Username,Email,Password required!', response.data)

    # Test accessing audio analyzing page without login
    def test_analyze_page_access(self):
        response = self.client.get('/Audio_Analysing', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login to the site to use this Audio Analysing functionality', response.data)

    # Test compressor page access without login
    def test_compressor_page_access(self):
        response = self.client.get('/compressor', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Loggin to the site to use this automatic audio mixer', response.data)

    # Test vocal isolation page access without login
    def test_isolation_page_access(self):
        response = self.client.get('/isolation', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'login to the site to use AI powered vocal isolation', response.data)

    # Test reverb page access without login
    def test_reverb_page_access(self):
        response = self.client.get('/reverb', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login to the site to use Reverb functionality', response.data)

if __name__ == '_main_':
    unittest.main()