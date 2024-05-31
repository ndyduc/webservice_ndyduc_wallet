from binance.client import Client

# Khóa API và bí mật API của bạn
api_key = 'yE9mJDopggg8DNWyAuqvJlww3sg4XxrEeZSBP6pLO4qnQsHfZhUrfUZfnFzHm9EU'
api_secret = '3D0QkNrccBNciBszseFFatBkghpJztOU2Z7k7zZuNAwqNOq5zuVdl0UcMiWW0L3u'

# Tạo một đối tượng client
client = Client(api_key, api_secret)

# Lấy thông tin tài khoản
account_info = client.get_account()

# In thông tin tài khoản
print(account_info)
