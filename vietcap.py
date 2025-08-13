import requests
import pandas as pd

class VietCapClient:
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Chrome/120.0.0.0",
        "Referer": "https://trading.vietcap.com.vn/"
    }
    today = pd.Timestamp.today().normalize()
    yesterday = today - pd.DateOffset(days=1)
    yesterday_yymmdd = yesterday.strftime("%Y-%m-%d")

    def query_graphql(self, query:str, variables={}, **kwargs):
        url = "https://trading.vietcap.com.vn/data-mt/graphql"
        default_params = {
            "variables": variables,
            "query": query
        }
        payload = {**default_params, **kwargs}
        response = requests.post(url, headers=self.headers, json=payload)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                return data.get("data", {})

    def get_stocks(self):
        query = """
            query Query {
            CompaniesListingInfo {
                id
                ticker
                organName
                organShortName
                enOrganName
                enOrganShortName
                comTypeCode
                icbCode1
                icbCode2
                icbCode3
                icbCode4
                tickerPriceInfo {
                    closePrice
                    exchange
                    totalVolume
                    averageMatchVolume2Week
                    averageVolume1Month
                }
                financialRatio {
                    ev
                    pe
                    pb
                    revenueGrowth
                    roa
                    roe
                    grossMargin
                    evPerEbitda
                }
            }
        }
        """
        data = self.query_graphql(query)
        if isinstance(data, dict):
            df = pd.json_normalize(data.get("CompaniesListingInfo"))
            df.rename(columns=lambda x: x[x.find(".")+1:] if isinstance(x,str) else x, inplace=True)
            return df

    def get_historical_price(self, ticker:str, from_date="2020-10-01", to_date=yesterday_yymmdd):
        query = """
            query Query($ticker: String!, $offset: Int!, $limit: Int!, $fromDate: String!, $toDate: String!) {
                TickerPriceHistory(
                    ticker: $ticker
                    offset: $offset
                    limit: $limit
                    fromDate: $fromDate
                    toDate: $toDate
                ) 
                {
                    history {
                        tradingDate
                        ticker
                        openPrice
                        highestPrice
                        lowestPrice
                        closePrice
                        openPriceAdjusted
                        highestPriceAdjusted
                        lowestPriceAdjusted
                        closePriceAdjusted
                        totalMatchVolume
                        totalMatchValue
                        totalDealVolume
                        totalDealValue
                        unMatchedBuyTradeVolume
                        unMatchedSellTradeVolume
                        totalVolume
                        totalValue
                        totalBuyTrade
                        totalBuyTradeVolume
                        totalSellTrade
                        totalSellTradeVolume
                    }
                }
            }
        """
        variables = {
            "ticker": ticker,
            "limit": 9999,
            "offset": 0,
            "fromDate": from_date,
            "toDate": to_date
        }
        data = self.query_graphql(query, variables=variables, operationName="Query")
        if isinstance(data, dict):
            return data.get("TickerPriceHistory", {"history":[]})["history"]
        else:
            return []

    def get_technical_assessment(self, ticker:str):
        url = "https://iq.vietcap.com.vn/api/iq-insight-service/v1/company/{}/technical/ONE_DAY".format(ticker)
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict):
                if data.get("status") == 200:
                    return data.get("data", {})