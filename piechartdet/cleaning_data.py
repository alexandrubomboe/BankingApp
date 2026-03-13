import pandas as pd

def clean_raw_df(df):
    df_clean = df.copy()
    cols_to_drop = ['Completed Date', 'Fee', 'Currency', 'State']
    df_clean.drop(columns=[c for c in cols_to_drop if c in df_clean.columns], inplace=True)
    
    rename_map = {
        'Type': 'type', 
        'Product': 'product', 
        'Started Date': 'date', 
        'Description': 'description', 
        'Amount': 'amount', 
        'Balance': 'balance'
    }
    df_clean.rename(columns=rename_map, inplace=True)
    df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
    
    return df_clean

def get_transfers_report(df, period_type: str, value: str):
    df = clean_raw_df(df)
    transfer = df[df['type'].str.contains('Transfer', case=False, na=False)]
    transfer = transfer[~transfer['description'].str.contains('pocket', case=False, na=False)].copy()
    
    if period_type == 'monthly':
        transfer['period'] = transfer['date'].dt.strftime('%Y-%m')
    else:
        transfer['period'] = transfer['date'].dt.strftime('%Y')
        
    filtered = transfer[transfer['period'] == value]
    received = filtered[filtered['amount'] > 0]['amount'].sum()
    sent = filtered[filtered['amount'] < 0]['amount'].sum()
    
    return {
        "money_sent": round(float(abs(sent)), 2),
        "money_received": round(float(received), 2)
    }

def get_spendings_report(df, period_type: str, value: str):
    df = clean_raw_df(df)
    spendings = df[df['amount'] < 0].copy()
    spendings['category'] = 'Other'

    categories_dict = {
        'Groceries': ['trei', 'Trading', 'uni door', 'mega image', 'profi', 'kaufland', 'lidl', 'carrefour', 'penny', 'auchan', 'cora', 'zeman', 'inmedio'],
        'Food&Coffee': ['ponis', 'facultatea', 'jeans', 'mcdonald', 'kfc', 'arabian', 'pizza hut', 'chopstix', 'fornetti', '5togo', 'starbucks', 'tazz', 'glovo', 'restaurant', 'pub', 'bistro', 'food', 'kitchen', 'festin', 'burger'],
        'Transport': ['uber', 'bolt', 'lime', 'splash', 'metrorex', 'cfr', 'ct bus', 'stb', 'wizz', 'ryanair', 'tarom', 'bilete'],
        'Auto': ['rompetrol', 'omv', 'petrom', 'mol', 'lukoil', 'socar', 'auto total'],
        'Entertainment': ['neversea', 'extasy', 'superbet', 'casa pariurilor', 'cinema', 'netflix', 'spotify', 'steam', 'playstation', 'hbo', 'xbox', 'events'],
        'Shopping': ['flanco', 'altex', 'emag', 'dedeman', 'ikea', 'jysk', 'pepco', 'zara', 'h&m'],
        'Utilities': ['enel', 'e.on', 'engie', 'digi', 'vodafone', 'orange', 'telekom', 'apa nova', 'radet', 'intretinere', 'electrica'],
        'Health': ['farmacia', 'catena', 'dr max', 'help net', 'medlife', 'regina maria', 'synevo'],
        'Transfers': ['to ', 'payment from']
    }

    for category, words in categories_dict.items():
        pattern = '|'.join(words)
        mask = spendings['description'].str.contains(pattern, case=False, na=False)
        spendings.loc[mask, 'category'] = category

    if period_type == 'monthly':
        spendings['period'] = spendings['date'].dt.strftime('%Y-%m')
    else:
        spendings['period'] = spendings['date'].dt.strftime('%Y')

    filtered = spendings[spendings['period'] == value]
    result = filtered.groupby('category')['amount'].sum().abs()
    
    return {cat: round(float(val), 2) for cat, val in result.sort_values(ascending=False).to_dict().items()}