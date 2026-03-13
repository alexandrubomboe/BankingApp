import pandas as pd
df = pd.read_csv('extras.csv')

# data scraping
df.drop(columns=['Completed Date', 'Fee', 'Currency', 'State'], inplace=True)
df.rename({'Type': 'type', 'Product': 'product', 'Started Date': 'date', 'Description': 'description', 'Amount':'amount', 'Balance': 'balance'}, axis=1, inplace=True)
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')

# total money sent/received each month
transfer = df[df['type'] == 'Transfer']
transfer = transfer[~transfer['description'].str.contains('pocket', case=False, na=False)]
transfer['month'] = transfer['date'].dt.to_period('M')

received_month = transfer[transfer['amount'] > 0].groupby('month')['amount'].sum()
sent_month = transfer[transfer['amount'] < 0].groupby('month')['amount'].sum().abs()

summary_month = pd.DataFrame({
	'Money Sent': sent_month,
	"Money Received": received_month
}).fillna(0)

target_month = input("Introdu luna si anul (format YYYY-MM)\n")
summary_month.index = summary_month.index.astype(str)
monthly = summary_month.loc[[target_month]]

print(f"\nRezumat pentru {target_month}:")
print(monthly.to_string(index=True))

#total money sent/received each year
transfer['year'] = transfer['date'].dt.to_period("Y")
received_year = transfer[transfer['amount'] > 0].groupby('year')['amount'].sum()
sent_year = transfer[transfer['amount'] < 0].groupby('year')['amount'].sum().abs()

summary_year = pd.DataFrame({
	'Money Sent': sent_year,
	'Money Received': received_year
}).fillna(0)

target_year = input("\nIntrodu anul (format YYYY)\n")
summary_year.index = summary_year.index.astype(str)
yearly = summary_year.loc[[target_year]]

print(f'\nRezumat pentru anul {target_year}:')
print(yearly.to_string(index=False))

# categorise foods
spendings = df[df['amount'] < 0].copy()
spendings['category'] = 'Other'

categories_dict =  {
	'Groceries': ['trei', 'Trading', 'uni door', 'mega image', 'profi', 'kaufland', 'lidl', 'carrefour', 'penny', 'auchan', 'cora', 'zeman', 'inmedio'],
	'Food&Coffee': ['ponis', 'facultatea', 'jeans', 'mcdonald', 'kfc', 'arabian', 'pizza hut', 'chopstix', 'fornetti', '5togo',\
					'starbucks', 'tazz', 'glovo', 'restaurant', 'pub', 'bistro', 'food', 'kitchen', 'festin', 'burger'],
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
	
spendings = spendings[['category', 'amount', 'date']]
spendings['amount'] = spendings['amount'].abs()

# monthly spendings
target_month = input("Introdu luna si anul:\n")
spendings['date'] = spendings['date'].astype(str)
mask = spendings['date'].str.contains(target_month, case=False, na=False)

result = spendings[mask]
result = result[['category', 'amount']]
result = result.groupby('category')['amount'].sum()
result.index.name = None
monthly_spendings_categorised = result.sort_values()

print(f"\nRezumat pentru {target_month}:")
print(monthly_spendings_categorised.to_string())

# yearly spendings
target_year = input("Introdu anul:\n")
mask = spendings['date'].str.contains(target_year, case=False, na=False)

result = spendings[mask]
result = result[['category', 'amount']]
result = result.groupby('category')['amount'].sum()
result.index.name = None
yearly_spendings_categorised = result.sort_values()

print(f"\nRezumat pentru anul {target_year}:\n")
print(yearly_spendings_categorised.to_string())