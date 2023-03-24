import pandas as pd

import altair as alt
import yfinance as yf
import streamlit as st

st.title('米国株価可視化アプリ')

st.sidebar.write('''
# GAFA株価
株価可視化ツール。以下のオプションから標示日数を指定してください
''')


st.sidebar.write('''
# 標示日数の選択
''')
days = st.sidebar.slider('日数',1 ,300, 20)

st.write(f"""
### 過去 **{days}日間** のGAFAの株価
""")

@st.cache_data
def get_data(days, tickers):
    df = pd.DataFrame()
    for company in tickers.keys():
        tkr = yf.Ticker(tickers[company])
        hist = tkr.history(period=f'{days}d')
        hist.index = hist.index.strftime('%d %B %Y')
        hist = hist[['Close']]
        hist.columns = [company]
        hist = hist.T
        hist.index.name = 'Name'
        df = pd.concat([df, hist])
    return df

try:
    st.sidebar.write("""
    ## 株価の範囲指定
    """)
    y_min, y_max = st.sidebar.slider('範囲を指定してください',
                      0.0, 3500.0, (0.0, 3500.0))

    tickers = {
        'apple': 'AAPL',
        'facebook': 'meta',
        'google': 'GOOGL',
        'microsoft': 'MSFT',
        'netflix': 'NFLX',
        'amazon': 'AMZN'
    }

    df = get_data(days, tickers)
    companies = st.multiselect(
        '会社名を選択',
        list(df.index),
        ['google', 'amazon', 'facebook', 'apple']
    )
    if not companies:
        st.error('少なくても1社は選んでください')
    else:
        data = df.loc[companies]
        st.write('### 株価（USD）', data.sort_index())
        data = data.T.reset_index()
        data = pd.melt(data, id_vars=['Date']).rename(
            columns={'value': 'Stock Prices(USD)'}
        )

        chart = (
            alt.Chart(data)
            .mark_line(opacity=0.8, clip=True)
            .encode(
                x='Date:T',
                y=alt.Y('Stock Prices(USD):Q', stack=None, scale=alt.Scale(domain=[y_min, y_max])),
                color='Name:N'
            )
        )
        st.altair_chart(chart, use_container_width=True)
except:
    st.error(
        'エラーが出ています'
        )
