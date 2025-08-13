# Backtest tín hiệu MUA tại phiên giao dịch gần nhất

## 1. Giới thiệu  
Dự án này thực hiện backtesting chiến lược mua cổ phiếu dựa trên tín hiệu MUA tại phiên giao dịch **hôm nay**.  
Quy trình bao gồm:  
- Lọc danh sách cổ phiếu có tín hiệu MUA.  
- Backtest hiệu suất của các mã đó.  
- Phân tích các chỉ số đánh giá như lợi nhuận, drawdown, tỷ lệ thắng, v.v.  

## 2. Yêu cầu hệ thống  
- Python == 3.10  
- pip >= 21.2.4
- Hệ điều hành: Windows / macOS / Linux

## 3. Cài đặt thư viện  
Cài đặt toàn bộ thư viện cần thiết:  
```bash
pip install -r requirements.txt
```

## 4. Tín hiệu MUA tại phiên giao dịch gần nhất

Một mã được chọn vào danh sách backtest nếu tại phiên **giao dịch gần nhất** đồng thời thỏa:

- `EV ≥ 1e12`
- `averageVolume3Month ≥ 2e5`
- **SMA10 cắt lên SMA20** (tức là hôm nay `SMA10 > SMA20` và hôm qua `SMA10 ≤ SMA20`)
- `SMA20 > SMA50`
- `SMA50 > SMA100`
- `MACD > MACDsignal`

> Lưu ý: Hai điều kiện **EV** và **averageVolume3Month** chỉ được dùng để **lọc ở hôm nay**; **không** dùng trong backtest lịch sử.

Ví dụ code (minh họa ý tưởng lọc *hôm nay*):
```python
import fialda import FialdaClient
payload = """
    {
        "faFilter": {
            "AvgVol3M": {
                "min": 200000,
                "max": null
            },
            "MarketCap": {
                "min": 1000000000000,
                "max": null
            },
            "TotalDealVol": {
                "min": null,
                "max": null
            },
            "LastPrice": {
                "min": null,
                "max": null
            }
        },
        "taFilter": null,
        "booleanFilter": {
            "AvailableForFASearching": true
        },
        "pageNumber": 1,
        "pageSize": 10000,
        "exchanges": [
            "HSX",
            "HNX",
            "UPCOM"
        ],
        "icbCodes": null,
        "sortColumn": "Symbol",
        "isDesc": false,
        "fAFilterSub": null,
        "faKeys": [
            "SMA10_VUOT_SMA20_Daily",
            "SMA10_>_SMA50_Daily",
            "MACD_>=_MACDSignal_Daily",
            "SMA20_>_SMA50_Daily",
            "SMA50_>_SMA100_Daily"
        ],
        "wlOrPId": null,
        "tradingTime": null
    }
"""
df_buy_signal = fialda.get_stock_data_by_filter(payload)
# -> Danh sách mã sẽ đem đi backtest
```

## 5. Backtesting các mã cổ phiếu đã lọc

Sau khi đã lọc được danh sách các mã cổ phiếu có tín hiệu **MUA** tại phiên giao dịch hôm nay, tiến hành backtest để đánh giá hiệu quả của chiến lược.

### 5.1. Chuẩn bị dữ liệu
- Thu thập dữ liệu giá lịch sử (OHLCV) cho các mã cổ phiếu đã lọc, ví dụ từ năm 2016 đến nay.
- Đảm bảo dữ liệu đầy đủ để tính được tất cả các chỉ báo kỹ thuật sử dụng trong chiến lược (SMA10, SMA20, SMA50, SMA100, MACD, MACD Signal).
- Loại bỏ 100 phiên đầu tiên để tránh dữ liệu bị thiếu do tính SMA100.

### 5.2. Xây dựng tín hiệu giao dịch
- Sử dụng lại các điều kiện lọc tín hiệu MUA, nhưng áp dụng cho toàn bộ chuỗi thời gian.
- Tạo Series `entries` (tín hiệu MUA) và `exits` (tín hiệu BÁN) dựa trên chiến lược.

### 5.3. Backtest với `vectorbt`
Ví dụ:

```python
import vectorbt as vbt

pf = vbt.Portfolio.from_signals(
    close=df["close"],
    entries=df["buySignal"],
    exits=df["sellSignal"],
    size=1.0,       # mua toàn bộ vốn cho mỗi lệnh
    fees=0.001,     # phí giao dịch 0.1%
    freq="1D"
)
```

## 6. Phân tích kết quả
- Sử dụng hàm **pf.stats()** để xem các chỉ số hiệu suất:
  - **Total Return**: Tỷ suất lợi nhuận tổng cộng.
  - **Sharpe Ratio**: Đo lường lợi nhuận điều chỉnh theo rủi ro.
  - **Max Drawdown**: Mức sụt giảm tối đa từ đỉnh.
  - **Win Rate**: Tỷ lệ lệnh giao dịch có lợi nhuận.
  - **Profit Factor**: Tỷ số tổng lợi nhuận / tổng thua lỗ.
    |                            | GIL                 | GVR                        | HPX                 | MSN                        | VCS                 | VOS                 |
    |:---------------------------|:--------------------|:---------------------------|:--------------------|:---------------------------|:--------------------|:--------------------|
    | Start                      | 2016-06-06 00:00:00 | 2018-08-10 00:00:00        | 2018-12-11 00:00:00 | 2016-06-06 00:00:00        | 2016-06-06 00:00:00 | 2016-06-06 00:00:00 |
    | End                        | 2025-08-12 00:00:00 | 2025-08-12 00:00:00        | 2025-08-12 00:00:00 | 2025-08-12 00:00:00        | 2025-08-12 00:00:00 | 2025-08-12 00:00:00 |
    | Period                     | 2298 days 00:00:00  | 1743 days 00:00:00         | 1663 days 00:00:00  | 2298 days 00:00:00         | 2299 days 00:00:00  | 2298 days 00:00:00  |
    | Start Value                | 100.0               | 100.0                      | 100.0               | 100.0                      | 100.0               | 100.0               |
    | End Value                  | 159.26              | 235.79                     | 95.29               | 94.73                      | 103.03              | 90.81               |
    | Total Return [%]           | 59.26               | 135.79                     | -4.71               | -5.27                      | 3.03                | -9.19               |
    | Benchmark Return [%]       | -21.29              | 330.68                     | -67.73              | 95.82                      | 91.84               | 654.55              |
    | Max Gross Exposure [%]     | 100.0               | 100.0                      | 100.0               | 100.0                      | 100.0               | 100.0               |
    | Total Fees Paid            | 2.13                | 2.9                        | 1.13                | 2.69                       | 1.23                | 0.7                 |
    | Max Drawdown [%]           | 43.08               | 15.93                      | 24.41               | 44.46                      | 22.18               | 39.29               |
    | Max Drawdown Duration      | 1083 days 00:00:00  | 500 days 00:00:00          | 992 days 00:00:00   | 1839 days 00:00:00         | 1464 days 00:00:00  | 1904 days 00:00:00  |
    | Total Trades               | 7                   | 9                          | 6                   | 11                         | 6                   | 3                   |
    | Total Closed Trades        | 7                   | 9                          | 6                   | 11                         | 6                   | 3                   |
    | Total Open Trades          | 0                   | 0                          | 0                   | 0                          | 0                   | 0                   |
    | Open Trade PnL             | 0.0                 | 0.0                        | 0.0                 | 0.0                        | 0.0                 | 0.0                 |
    | Win Rate [%]               | 57.14               | 77.78                      | 16.67               | 36.36                      | 50.0                | 33.33               |
    | Best Trade [%]             | 61.46               | 37.67                      | 13.94               | 29.46                      | 14.91               | 35.93               |
    | Worst Trade [%]            | -25.43              | -2.77                      | -8.87               | -20.55                     | -12.97              | -23.01              |
    | Avg Winning Trade [%]      | 32.58               | 14.53                      | 13.94               | 13.66                      | 7.51                | 35.93               |
    | Avg Losing Trade [%]       | -17.24              | -2.53                      | -3.47               | -7.36                      | -5.81               | -18.13              |
    | Avg Winning Trade Duration | 52 days 18:00:00    | 35 days 13:42:51.428571428 | 26 days 00:00:00    | 30 days 18:00:00           | 31 days 16:00:00    | 28 days 00:00:00    |
    | Avg Losing Trade Duration  | 12 days 00:00:00    | 18 days 12:00:00           | 13 days 04:48:00    | 11 days 06:51:25.714285714 | 20 days 16:00:00    | 9 days 12:00:00     |
    | Profit Factor              | 1.53                | 14.65                      | 0.72                | 0.92                       | 1.17                | 0.8                 |
    | Expectancy                 | 8.47                | 15.09                      | -0.79               | -0.48                      | 0.5                 | -3.06               |
    | Sharpe Ratio               | 0.48                | 0.96                       | -0.04               | 0.03                       | 0.1                 | -0.08               |
    | Calmar Ratio               | 0.18                | 1.23                       | -0.04               | -0.02                      | 0.02                | -0.04               |
    | Omega Ratio                | 1.23                | 1.41                       | 0.97                | 1.01                       | 1.07                | 0.93                |
    | Sortino Ratio              | 0.72                | 1.62                       | -0.06               | 0.03                       | 0.13                | -0.11               |

- Sử dụng **pf.plot().show()** để trực quan hóa đường vốn (equity curve) và các lệnh giao dịch trên biểu đồ. *Ví dụ*, mã **GVR**

    ![Kết quả backtesting](backtesting_plot.png)

## 7. Diễn giải
- So sánh kết quả giữa các mã cổ phiếu đã backtest.
- Đánh giá xem chiến lược có ổn định và khả thi hay không trong nhiều điều kiện thị trường khác nhau.
- Xem xét điều chỉnh tham số (SMA, MACD) hoặc kết hợp thêm các bộ lọc để cải thiện hiệu suất.