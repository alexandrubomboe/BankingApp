from fastapi import FastAPI
import pandas as pd
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitem comunicarea cu interfata web a prietenului tau
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- INCARCARE SI CURATARE DATE (Se executa o singura data) ---
df = pd.read_csv('extras.csv')
df.drop(columns=['Completed Date', 'Fee', 'Currency', 'State'], inplace=True, errors='ignore')
df.rename(columns={'Type': 'type', 'Product': 'product', 'Started Date': 'date', 'Description': 'description', 'Amount':'amount', 'Balance': 'balance'}, inplace=True)
df['date'] = pd.to_datetime(df['date'])

# Pregatire Transferuri (Sent/Received)
transfer = df[df['type'] == 'Transfer'].copy()
transfer = transfer[~transfer['description'].str.contains('pocket', case=False, na=False)]
transfer['month'] = transfer['date'].dt.to_period('M').astype(str)
transfer['year'] = transfer['date'].dt.to_period('Y').astype(str)

# Pregatire Categorisire Spendings
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
    'Health ': ['farmacia', 'catena', 'dr max', 'help net', 'medlife', 'regina maria', 'synevo'],
    'Transfers': ['to ', 'payment from']
}

for category, words in categories_dict.items():
    pattern = '|'.join(words)
    mask = spendings['description'].str.contains(pattern, case=False, na=False)
    spendings.loc[mask, 'category'] = category

spendings['amount'] = spendings['amount'].abs()
spendings['month'] = spendings['date'].dt.to_period('M').astype(str)
spendings['year'] = spendings['date'].dt.to_period('Y').astype(str)

# --- ENDPOINT-URI PENTRU FRONTEND ---

@app.get("/summary/month/{target_month}")
def get_monthly(target_month: str):
    # 1. Sent/Received (Logica ta de Transfer)
    t_month = transfer[transfer['month'] == target_month]
    received = t_month[t_month['amount'] > 0]['amount'].sum()
    sent = t_month[t_month['amount'] < 0]['amount'].abs().sum()
    
    # 2. Spendings per Category (Logica ta de spendings)
    s_month = spendings[spendings['month'] == target_month]
    cat_result = s_month.groupby('category')['amount'].sum().sort_values()
    
    return {
        "target": target_month,
        "money_sent": float(sent),
        "money_received": float(received),
        "categorised_spendings": cat_result.to_dict()
    }

@app.get("/summary/year/{target_year}")
def get_yearly(target_year: str):
    # 1. Sent/Received (Logica ta de Transfer)
    t_year = transfer[transfer['year'] == target_year]
    received = t_year[t_year['amount'] > 0]['amount'].sum()
    sent = t_year[t_year['amount'] < 0]['amount'].abs().sum()
    
    # 2. Spendings per Category (Logica ta de spendings)
    s_year = spendings[spendings['year'] == target_year]
    cat_result = s_year.groupby('category')['amount'].sum().sort_values()
    
    return {
        "target": target_year,
        "money_sent": float(sent),
        "money_received": float(received),
        "categorised_spendings": cat_result.to_dict()
    }

@app.get("/health")
def health():
    return {"status": "online", "data_points": len(df)}