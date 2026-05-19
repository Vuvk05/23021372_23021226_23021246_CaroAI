Chương trình chơi cờ Caro giữa người và máy, sử dụng thuật toán Minimax và Alpha-Beta Pruning.

## Yêu cầu

- Python 3.8 - 3.11
- pygame (không tương thích với 3.14)

```bash
pip install -r requirements.txt
```

## Cách chạy

### Chạy game (giao diện pygame)

```bash
cd source_code
python main.py
```

### Chạy benchmark thực nghiệm (Level 3)

```bash
cd source_code
python benchmark.py
```

## Hướng dẫn chơi

- Click vào ô trống trên bàn cờ để đánh quân **X** (người chơi)
- Máy tự động đánh quân **O** sau mỗi lượt
- Chọn **thuật toán** (Minimax / Alpha-Beta) và **độ sâu** (D=1..4) trên panel bên phải
- Nhấn **Ván mới** để bắt đầu lại
- Nhấn **Benchmark** để chạy phân tích thực nghiệm trong terminal

## Luật chơi

- Bàn cờ 9×9
- Người thắng khi có **4 quân liên tiếp** (ngang, dọc, chéo)
- Không áp dụng luật chặn hai đầu
- Hòa khi bàn cờ đầy

## Cấu trúc project

```
source_code/
├── main.py        # Giao diện pygame, vòng lặp game
├── game.py        # Logic bàn cờ, kiểm tra thắng/thua
├── ai.py          # Minimax và Alpha-Beta pruning
├── evaluate.py    # Hàm đánh giá trạng thái bàn cờ
└── benchmark.py   # Thực nghiệm Level 3
requirements.txt
report.pdf
README.md
```
