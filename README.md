# Caro AI

Game cờ Caro 9×9 với AI sử dụng Minimax và Alpha-Beta Pruning, viết bằng Python + Pygame.

## Luật chơi

- Bàn cờ **9×9**
- Thắng khi có **4 quân liên tiếp** (ngang / dọc / chéo)
- Không áp dụng luật chặn 2 đầu

---

## Cài đặt & Cách chạy

### Cách 1: Chạy bằng file `.exe` (Windows, không cần cài Python)

> Dành cho người dùng phổ thông, không cần biết lập trình.

1. Giải nén file ZIP về máy.
2. Vào thư mục `source_code/`.
3. Double-click vào file **`CaroAI.exe`** để chạy trực tiếp.

>  Nếu Windows hiện cảnh báo "Windows protected your PC", nhấn **More info → Run anyway** để tiếp tục.

---

### Cách 2: Chạy bằng Python (Windows / macOS / Linux)

> Dành cho người có cài Python, hoặc muốn chỉnh sửa source code.

#### Yêu cầu

- Python **3.10** trở lên → tải tại [python.org](https://www.python.org/downloads/)

#### Bước 1 – Giải nén và mở terminal

```bash
cd 23021304_23021324_CaroAI-main
```

#### Bước 2 – Cài thư viện

```bash
pip install -r requirements.txt
```

#### Bước 3 – Chạy game

```bash
cd source_code
python main.py
```

> **macOS / Linux:** nếu máy có cả Python 2 và 3, dùng `python3 main.py`.

---

## Hướng dẫn sử dụng

### Màn hình Menu chính

Sau khi khởi động, chọn 1 trong 5 chế độ chơi:

| Số | Tên chế độ | Mô tả |
|----|------------|-------|
| 0 | **Human vs Human** | 2 người chơi luân phiên trên cùng máy |
| 1 | **Human vs Minimax** | Đấu với AI Minimax thuần (không cắt nhánh) |
| 2 | **Human vs AlphaBeta** | Đấu với AI Minimax + Alpha-Beta Pruning |
| 3 | **So sánh song song** | 2 AI tính cùng lúc, hiển thị song song để so sánh tốc độ |
| 4 | **Ultimate AI** | AlphaBeta + Iterative Deepening + Transposition Table (mạnh nhất) |

### Trong ván cờ

- **Click chuột trái** vào ô bất kỳ trên bàn cờ để đặt quân.
- **Panel bên phải** cho phép:
  - Chọn **You First** (đi trước, quân X) hoặc **AI First** (đi sau, quân O).
  - Chọn độ khó: **Easy** / **Medium** / **Hard** (tương ứng độ sâu tìm kiếm 1 / 2 / 3).
  - Thay đổi lựa chọn sẽ tự động reset ván mới.

---

## Các màn hình

| Mục | Tên | Mô tả |
|-----|-----|--------|
| 0 | Human vs Human | 2 người chơi luân phiên trên cùng máy |
| 1 | Human vs Minimax | Human đấu với Minimax thuần (không cắt nhánh) |
| 2 | Human vs AlphaBeta | Human đấu với Minimax + Alpha-Beta Pruning |
| 3 | So sánh song song | 2 AI tính cùng lúc, hiển thị song song để so sánh |
| 4 | Ultimate AI | AlphaBeta + Iterative Deepening + Transposition Table (mạnh nhất) |

---

## Tính năng

- **Chọn lượt đi trước / sau**: Ở các chế độ có AI (Minimax, AlphaBeta, Ultimate), người chơi có thể chọn **You First** (đi trước, quân X) hoặc **AI First** (đi sau, quân O) ngay trên panel bên phải. Thay đổi lựa chọn sẽ tự động reset ván mới.
- **Chọn độ khó**: Easy / Medium / Hard tương ứng độ sâu tìm kiếm 1 / 2 / 3.
- **Tie-breaking**: Cùng điểm số → ưu tiên ô gần trung tâm bàn cờ.

---

## Cấu trúc thư mục

```
source_code/
├── main.py              # Entry point
├── config.py            # Cấu hình toàn cục (kích thước, màu sắc, điểm số)
├── CaroAI.exe           # File thực thi Windows (chạy thẳng, không cần Python)
├── core/
│   ├── board.py         # Quản lý trạng thái bàn cờ
│   ├── rules.py         # Kiểm tra thắng / hoà
│   └── moves.py         # Sinh nước đi + sắp xếp ưu tiên (phòng thủ trước)
├── ai/
│   ├── eval.py          # Hàm đánh giá thế cờ (heuristic)
│   ├── minimax.py       # Thuật toán Minimax thuần
│   └── alphabeta.py     # Minimax + Alpha-Beta Pruning + Transposition Table
└── ui/
    ├── common.py            # Widget dùng chung (Button, MoveLog, font)
    ├── board_widget.py      # Vẽ bàn cờ, animation đặt quân
    ├── screen_menu.py       # Màn menu chính
    ├── screen_hvh.py        # Human vs Human
    ├── screen_minimax.py    # Human vs Minimax
    ├── screen_alphabeta.py  # Human vs AlphaBeta
    ├── screen_compare.py    # So sánh song song
    └── screen_ultimate.py   # Ultimate AI
```

---

## Thuật toán AI

### Minimax
- Duyệt cây trò chơi đến độ sâu `d`, không cắt nhánh
- Độ phức tạp: O(b^d) với b là branching factor
- Dùng làm baseline so sánh

### Alpha-Beta Pruning
- Cắt nhánh không cần thiết khi `alpha >= beta`
- Giảm trung bình **90–95%** số node so với Minimax
- Có Transposition Table để tránh tính lại trạng thái đã gặp

### Ultimate AI
- AlphaBeta + Iterative Deepening: tìm kiếm từ độ sâu 1 tăng dần, lấy kết quả tốt nhất trong thời gian cho phép
- Độ sâu động theo số nước đã đi (đầu ván nông hơn, cuối ván sâu hơn)

### Heuristic đánh giá (`eval.py`)
Mỗi chuỗi quân được gán điểm theo độ dài và độ mở:

| Loại | AI | Địch |
|------|----|------|
| 4 liên tiếp (thắng) | +1,000,000 | −1,000,000 |
| 3 mở 2 đầu | +10,000 | −20,000 |
| 3 đóng 1 đầu | +2,000 | −4,000 |
| 2 mở 2 đầu | +1,000 | −1,500 |

### Ưu tiên phòng thủ
Mỗi lượt AI thực hiện 3 bước theo thứ tự:
1. **Kiểm tra AI thắng ngay** → đánh luôn
2. **Kiểm tra địch thắng ngay** → chặn ngay (bắt buộc)
3. **Minimax / AlphaBeta** tìm nước tối ưu

---

## Cấu hình (`config.py`)

```python
BOARD_SIZE       = 9       # Kích thước bàn cờ
WIN_LENGTH       = 4       # Số quân cần để thắng
CANDIDATE_RADIUS = 2       # Bán kính tìm nước đi xung quanh quân đã đặt
DEPTHS = {"Easy": 1, "Medium": 2, "Hard": 3}
```

---

## Yêu cầu hệ thống

- OS: Windows / macOS / Linux
- RAM: tối thiểu 256 MB
- Python: 3.10+ *(chỉ cần nếu chạy bằng Python)*
