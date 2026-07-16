import unittest
import io
import json
from unittest.mock import patch
from app import app, SECRET_KEY
import jwt
import datetime

class TestProductUploads(unittest.TestCase):
    def setUp(self):
        # Thiết lập test client
        self.client = app.test_client()
        self.client.testing = True

        # Tạo một JWT Token giả lập tài khoản admin để pass được check_is_admin()
        token = jwt.encode({
            "username": "admin",
            "role": "admin",
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
        }, SECRET_KEY, algorithm="HS256")
        
        self.headers = {
            'Authorization': f'Bearer {token}'
        }

    def test_upload_invalid_extension(self):
        # TC5.1: Gửi một file không có đuôi ảnh hợp lệ (VD: file .txt)
        data = {
            'name': 'Sản phẩm test',
            'price': '1000',
            'image_file': (io.BytesIO(b"some random text"), 'malicious_script.sh')
        }
        
        response = self.client.post(
            '/api/admin/products', 
            data=data, 
            headers=self.headers,
            content_type='multipart/form-data'
        )
        
        # Mong đợi mã lỗi 400 Bad Request
        self.assertEqual(response.status_code, 400)
        
        res_data = json.loads(response.data)
        self.assertFalse(res_data['success'])
        self.assertIn('Định dạng file không được hỗ trợ', res_data['message'])

    @patch('werkzeug.datastructures.FileStorage.save')
    def test_upload_corrupted_file_save_error(self, mock_save):
        # TC5.2: Gửi file có đuôi hợp lệ, nhưng quá trình lưu đĩa cứng bị lỗi
        # Chúng ta dùng "mock" để ép hàm save() văng ra lỗi (giả lập disk full hoặc file corrupted part-way)
        mock_save.side_effect = Exception("Giả lập lỗi hỏng file không thể đọc/ghi")
        
        data = {
            'name': 'Loa Array',
            'price': '5000',
            # Gửi dữ liệu rác (invalid bytes)
            'image_file': (io.BytesIO(b"\x00\x01\x02\x03\xFF\xFF"), 'corrupted_image.png')
        }

        response = self.client.post(
            '/api/admin/products', 
            data=data, 
            headers=self.headers,
            content_type='multipart/form-data'
        )

        # Mong đợi không bị crash (không ra lỗi 500) mà trả về 400 do khối try...except
        self.assertEqual(response.status_code, 400)
        
        res_data = json.loads(response.data)
        self.assertFalse(res_data['success'])
        self.assertEqual(res_data['message'], "Lưu file thất bại, file có thể bị hỏng. Vui lòng thử lại!")

if __name__ == '__main__':
    unittest.main()
