from django.test import TestCase
from django.db import connection


class DatabaseConnectionTest(TestCase):
    def test_database_connection(self):
        # Kiểm tra kết nối đến cơ sở dữ liệu
        self.assertTrue(connection.connection)

        # Lấy tên cơ sở dữ liệu
        db_name = connection.settings_dict['NAME']
        self.assertEqual(db_name, 'test_ndyduc_wallet')
        print("Yeah, that fucking shit is done !!!")
