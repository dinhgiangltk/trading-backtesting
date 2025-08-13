import requests
import pandas as pd

class FialdaClient:
    headers = {
        "content-type": "application/json;charset=UTF-8",
        "user-agent": "Chrome/122.0.0.0",
    }
    def get_stock_data_by_filter(self, payload:str):
        url = "https://fwtapi3.fialda.com/api/services/app/Stock/GetDataByFilter"
        response = requests.post(url, headers=self.headers, data=payload)
        data = response.json()
        if isinstance(data, dict):
            result = data.get("result")
            if isinstance(result, dict):
                total_items = result.get("totalCount", 0)
                items = result.get("items", [])
                if total_items > 0:
                    df = pd.DataFrame(items)
                    return df