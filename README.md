# webservice_ndyduc_wallet
Trường đại học Xây dựng Hà Nội
Khoa Công nghệ Thông tin
Bộ môn Công nghệ Phần mềm
🙡🕮🙣
 
BÁO CÁO ĐỒ ÁN
PHÁT TRIỂN ỨNG DỤNG DI ĐỘNG

Đề tài: Ứng dụng ví crypto

Nhóm 24 – Lớp 66pm3
Thành viên	Nguyễn Duy Đức	43665
Giảng viên hướng dẫn: Nguyễn Thanh Bản


Hà Nội, 05-2024 
Mục Lục
_ndyduc_ wallet
Mục Lục	2
Phần 1. Đặt vấn đề và định hướng giải pháp	3
A, Đặt vấn đề	3
B, Định hướng giải pháp	3
C, Cơ sở lý thuyết và công cụ lựa chọn	3
Phần 2. Các kết quả đạt được	4
A, Mô tả Sơ lược	4
B, Thiết kế cơ sở dữ liệu	5
- Bảng người dùng (User) :	5
- Bảng ví (Wallet) :	5
- Bảng thông báo (Inform) :	5
- Bảng coin (Coin) :	6
- Bảng biểu mẫu (Template) :	6
- Bảng lịch sử giao dịch (History) :	6
C, Product backlog	7
D, Usecase	8
1, Đăng nhập	8
2, Trang Market	9
3, Trang ví sở hữu	10
4, chức năng chuyển khoản	11
E,  Class Diagram	12
F, Sequence	13
1, Thêm network	13
2, Hiện các bài báo liên quan	13
3, Chuyển khoản	14
G, Thành phẩm	16
H, Kết luận	33
1. Kinh nghiệm tích luỹ:	33
2. Tương lai của ứng dụng:	33
3. Học hỏi và cải thiện:	33


 
Phần 1. Đặt vấn đề và định hướng giải pháp
A, Đặt vấn đề
	Hiện nay, các nền tảng blocktrain chỉ đang hỗ trợ chuyển khoản trong nội bộ. Các ứng dụng hỗ trợ chuyển khoản đa nền tảng mà chiếm được lòng tin của người dùng hiện đang rất hạn chế mà cơ hội lẫn tiềm năng từ thị trường ảo ngày càng cao.
B, Định hướng giải pháp
Tạo điều kiện thuận lợi cho các giao dịch trên Blockchain: Mã thông báo tiền điện tử nhằm mục đích thể hiện sự quan tâm đến một tài sản và tạo điều kiện thuận lợi cho các giao dịch trên blockchain. Chúng thậm chí có thể đại diện cho các loại tiền điện tử khác, chẳng hạn như mã thông báo tiền điện tử bằng một lượng bitcoin cụ thể trên một chuỗi khối cụ thể.
Khả năng chuyển nhượng và khả năng giao dịch: Mã thông báo tiền điện tử có thể giao dịch và chuyển nhượng giữa những người tham gia khác nhau, cho phép các nhà đầu tư sử dụng chúng cho nhiều mục đích khác nhau.
Hỗ trợ các loại token và chức năng khác nhau: ứng dụng có thể được thiết kế để hỗ trợ nhiều loại token và chức năng khác.
Kiểm soát : Ứng dụng có thể cung cấp cho người dùng toàn quyền kiểm soát tiền điện tử của họ, cho phép họ chuyển, lưu trữ và quản lý tài sản của mình một cách an toàn.
Thông tin kịp thời : Úng dụng cung cấp các bản tin, giá thi trường theo thời gian thực, giúp nguời dùng dễ đàng cập nhật được các thông tin mới nhất về thị trường, tạo cơ hội nắm bắt thị trường để có thể tạo ra thêm giá trị tài sản.
Đa nền tảng : Ứng dụng hỗ trợ liên kết với nhiều nền tảng blockchain khác nhau, giúp người dùng có thể trao đổi giữa nhiều nền tảng, dễ dàng chuyển đổi tài sản giữa nhiều nền tảng khác nhau.
Tóm lại, việc tạo một ứng dụng để chuyển tiền/mã thông báo tiền điện tử có thể cung cấp cho người dùng một nền tảng thuận tiện và an toàn để tương tác với nhiều loại tiền điện tử khác nhau, tạo điều kiện thuận lợi cho các giao dịch và quản lý tài sản kỹ thuật số của họ một cách hiệu quả.
C, Cơ sở lý thuyết và công cụ lựa chọn
Mục tiêu của App là tạo ra một nền tảng trung gian giúp người dùng dễ dàng trao đổi giữa các nền tảng khác nhau, cung cấp các thông tin liên quan đến thị trường, tỉ giá của tài sản (timeframe ) theo thời gian thực. Lấy ra các tài sản sở hữu trong tài sản liên kết kèm theo tổng tài sản hiện có. Cung cấp các chức năng phụ như thông báo, lịch sử giao dịch, lưu mẫu chuyển khoản.
Tài khoản người dùng được tạo dựa trên số điện thoại và xác thực bằng email.
người dùng xác thực giao dịch, thay mật khẩu cần nhập mã xác thực được gửi đến email
Công cụ : 	App phía client : Java Android
			Web server : Python Django
			Cơ sở dữ liệu : Mysql
			API : Kraken, Coindesk.

Phần 2. Các kết quả đạt được 
A, Mô tả Sơ lược 
	Khi khởi động app người dùng sẽ đi vào trang đăng nhập, sau đó bấm ‘Sign up’ để đăng ký tài khoản. Ở trang đăng ký người dùng cần điền đầy dủ thông tin và đặc biệt là email, sau đó hệ thống sẽ gửi một mã xác thực tới email đăng ký, người dùng cần nhập lai mã xác thực đó vào app để hoàn tất đăng ký. Trở về với trang đăng nhập, người dùng trực tiếp đăng nhập bằng tài khoản sở hữu. Trong trường hợp người dùng quên mật khẩu thi bấm vào ‘forgot password’ để đặt lai mật khẩu, người dùng sẽ cần nhập mã xác thực tới email để đặt lại mật khẩu.
	Khi đăng nhập hoàn tất, hệ thống sẽ đưa người dùng vào trang chủ, ở đây sẽ bao gồm một số chức năng chính như: Chuyển khoản, chuyển đổi tài sản, lịch sử giao dịch, thêm nền tảng blockchain,.. ngoài ra trang chủ còn cung cấp thông tin giá trị tài khoản gốc và kềm theo các bài báo mới nhất về thị trường. noài ra người dùng có thể chuyển đổi sang các trang khác trên thanh bar của ứng dụng.
	Tại trang Market cung cấp cho người dùng góc nhìn trực quan về tỉ giá của thị trường được cập nhật theo thời gian thực, người dùng có thể trực tiếp điều chinh bảng tỉ giá sao cho phù hợp với yêu cầu của mình.
	Tại trang Wallet là nơi hiện thị tài sản sở hữu của tài khoản gồm Tên, logo, giá hiện tại, tăng giảm bao nhiêu so với đầu phiên giao dịch. Người dùng có thể di chuyển qua lại giữa các ví một cách linh hoạt.
	Tại trang Profile là nơi người dùng có thể thay đổi các thông tin cá nhân như mật khẩu, email và một số chức năng phụ khác và người dùng có thể đăng xuất ở đây luôn.
	 
B, Thiết kế cơ sở dữ liệu
- Bảng người dùng (User) :
+ ID ( khóa chính, tự động thêm)
+ Số điện thoại ( char[20], không được giống nhau)
+ Name ( char[100] )
+ Email ( char[254], dùng để xác thực)
+ Pasword (char[100], mật khẩu tài khoản)
+ FA (char[6], lưu mã xác thực)

- Bảng ví (Wallet) :
+ wallet_id ( char[10], khóa chính)
+ user ( kiểu: User, khóa phụ tới bảng người dùng)
+ kind ( char[100], loại ví)
+ public_key ( char[1000], khóa API public)
+ private_key ( char[5000ư, khóa API private)

- Bảng thông báo (Inform) :
+ id ( khóa chính, tự động thêm)
+ user ( kiểu: User, khóa phụ tới bảng người dùng)
+ content ( char[5000], nội dung thông báo)
+ datetime ( Datetime, tự động thêm)



- Bảng coin (Coin) :
+ Coin_id ( khóa chính, tự động tăng)
+ user ( kiểu: User, khóa phụ tới bảng User)
+ wallet ( kiểu: Wallet, khóa phụ tới bảng Wallet)
+ currency ( char[50], tên coin)
+ amount ( Decimal, số lượng có)

- Bảng biểu mẫu (Template) :
+ id ( khóa chính, tự động tăng)
+ user ( kiểu: User, khóa phụ tới bảng người dùng)
+ gained_username ( char[100], tên người dùng đích)
+ wallet_id ( char[100], số tài khoản đích)
+ wallet_kind ( char[20], loại tài khoản đích)

- Bảng lịch sử giao dịch (History) :
+ id ( khóa chính tự động tăng)
+ user ( kiểu: User, khóa phụ tới bảng người dùng)
+ datetime ( Datetime, tự động thêm)
+ flag ( int, 1: chuyển khoản, 0: chuyển đổi)
+ wallet_id ( char[100], số ví chuyển)
+ currency ( char[10], tên coin)
+ amount ( Char[100], số lượng chuyển)
+ to_id ( char[100], số ví nhận)
+ message ( char[1000], Null, tin nhắn)

C, Product backlog
 



D, Usecase
1, Đăng nhập
 
2, Trang Market

 
 
3, Trang ví sở hữu

 
 
4, chức năng chuyển khoản

 
E,  Class Diagram
 
F, Sequence
1, Thêm network
 
2, Hiện các bài báo liên quan
 
3, Chuyển khoản
 
4, Chuyển đổi
 

G, Thành phẩm	
 	 	
          Trang đăng nhập					Hiện mật khẩu	



 		 
Trang đăng nhập nếu từng đăng nhập 			 	sai mật khẩu
 		 
   	      nhập mã xác thực			    	    gửi lại mã xác thực


Verify code gửi đến email
 
 		 
		Trang đăng ký				    Trang thông báo
 		 
Reset mật khẩu					Trang chủ





 		 
Trang thị trường					Thay đổi token







 		 	
Trang chuyển khoản					Sau khi chọn ví	






 		 
Sau khi chon token						Xác nhận
 		 
	Chuyển khoản thanh công				Lưu biểu mẫu
 		 
	Trang chuyển đổi					        chọn thông tin
 		 
	Xác nhận chuyển đổi				chuyển đổi thành công
 		 
     Trang thêm tài khoản Kraken				Trang lịch sử giao dịch
 		 
	Trang ví sở hữu						Chọn ví


 		 
Trang cá nhân						Đăng xuất
 		 
	Trang quản lý ví						Xóa ví

 		 
	Trang biểu mẫu						Xóa biểu mẫu
 		 
	Xác nhận xóa						xóa thành công
 
H, Kết luận
1. Kinh nghiệm tích luỹ:
Quá trình phát triển ứng dụng điện tử đã cung cấp cho em một lượng kinh nghiệm đáng kể về việc xây dựng và triển khai ứng dụng trên nền tảng di động.
Em đã học được cách tương tác với các thành phần cụ thể của hệ thống Android, từ giao diện người dùng đến quản lý dữ liệu và xử lý sự kiện.

2. Tương lai của ứng dụng:
Trải qua quá trình phát triển, em nhận ra cơ hội để mở rộng và cải thiện ứng dụng trong tương lai. Điều này có thể bao gồm việc thêm tính năng mới, tối ưu hóa hiệu suất, hoặc cải thiện giao diện người dùng.
+ Chuyển khoản bằng mã QR
+ Cung cấp API cho thanh toán

3. Học hỏi và cải thiện:
Quá trình phát triển ứng dụng đã mở ra một hành trình không ngừng học hỏi và cải thiện kỹ năng.
Tiếp tục nắm bắt các xu hướng công nghệ mới và áp dụng chúng vào ứng dụng để duy trì sự cạnh tranh và phát triển bền vững.
Trên hết, việc làm một ứng dụng điện tử không chỉ là về việc tạo ra một sản phẩm, mà còn là về quá trình học hỏi và trải nghiệm, đồng thời mở ra nhiều cơ hội phát triển trong tương lai.
