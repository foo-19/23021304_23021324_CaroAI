# 23021304_23021324_CaroAI
# Caro AI

Game cờ Caro 15×15 với AI sử dụng Minimax và Alpha-Beta Pruning, viết bằng Python + Pygame.

## Luật chơi

- Bàn cờ 15×15
- Thắng khi có **4 quân liên tiếp** (ngang / dọc / chéo)
- Không áp dụng luật chặn 2 đầu

---

## Cài đặt

### Yêu cầu
- Python 3.10 trở lên

### Cài thư viện
```bash
pip install -r requirements.txt
```

### Chạy game
```bash
cd source_code
python main.py
```

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

## Cấu trúc thư mục

```
source_code/
├── main.py              # Entry point
├── config.py            # Cấu hình toàn cục (kích thước, màu sắc, điểm số)
├── core/
│   ├── board.py         # Quản lý trạng thái bàn cờ
│   ├── rules.py         # Kiểm tra thắng / hoà
│   └── moves.py         # Sinh nước đi + sắp xếp ưu tiên (phòng thủ trước)
├── ai/
│   ├── eval.py          # Hàm đánh giá thế cờ (heuristic)
│   ├── minimax.py       # Thuật toán Minimax thuần
│   └── alphabeta.py     # Minimax + Alpha-Beta Pruning + Transposition Table
└── ui/
    ├── common.py        # Widget dùng chung (Button, MoveLog, font)
    ├── board_widget.py  # Vẽ bàn cờ, animation đặt quân
    ├── screen_menu.py   # Màn menu chính
    ├── screen_hvh.py    # Human vs Human
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
BOARD_SIZE       = 15      # Kích thước bàn cờ
WIN_LENGTH       = 4       # Số quân cần để thắng
CANDIDATE_RADIUS = 3       # Bán kính tìm nước đi xung quanh quân đã đặt
DEPTHS = {"Easy": 1, "Medium": 2, "Hard": 3}
```

---

## Yêu cầu hệ thống

- OS: Windows / macOS / Linux
- RAM: tối thiểu 256 MB
- Python: 3.10+
