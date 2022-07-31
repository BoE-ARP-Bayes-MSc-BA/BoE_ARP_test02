#%%
import pandas as pd
import yfinance as yf
from yahoofinancials import YahooFinancials

#%%
def stock_price_change(stock_list, start_date, end_date):
    # function for find price change
    def price_change(aapl_df, n_day):
        before = []
        after = []
        for i in range(len(aapl_df)):
            # price on that date
            prc_tdy = aapl_df['Close'][i]

            if ((i >= n_day) & 
                (i < (len(aapl_df)-n_day))):
                # price change before n_day
                prc_before = aapl_df['Close'][i-n_day]
                prc_change_before = (prc_tdy - prc_before)/prc_before
                # price change after n_day
                prc_after = aapl_df['Close'][i+n_day]
                prc_change_after = (prc_after - prc_tdy)/prc_tdy
            else:
                prc_change_before = 0
                prc_change_after = 0
            # append into list
            before.append(prc_change_before)
            after.append(prc_change_after)
        return before, after
        
    # tickers and its closing stock price
    stock_df = pd.DataFrame()
    for i in stock_list:
        aapl_df = yf.download(i, 
                        start= start_date,  # start='2010-12-01', # start 1 month before
                        end = end_date,   # end='2022-01-30', # end 1 month later
                        progress=False,)
        aapl_df = aapl_df.reset_index(drop=False)
        # add ticker name
        aapl_df['ticker']=i
        # add price change
        #aapl_df['D0'] = aapl_df['Close']
        aapl_df['D-1'],aapl_df['D+1'] = price_change(aapl_df, 1)
        aapl_df['D-2'],aapl_df['D+2'] = price_change(aapl_df, 2)
        aapl_df['D-3'],aapl_df['D+3'] = price_change(aapl_df, 3)
        aapl_df['D-5'],aapl_df['D+5'] = price_change(aapl_df, 5)
        aapl_df['D-10'],aapl_df['D+10'] = price_change(aapl_df, 10)
        aapl_df['D-15'],aapl_df['D+15'] = price_change(aapl_df, 15)
        # append into one dataframe 
        stock_df = stock_df.append(aapl_df)
        
    # drop redundancy columns
    stock_price_df = stock_df.drop(columns=['Open', 'High','Low','Adj Close','Volume'])
    stock_price_df = stock_price_df.rename(columns={'Date': 'date'})
    # drop duplicated rows
    stock_price_df = stock_price_df.drop_duplicates()
    return stock_price_df

# %%
