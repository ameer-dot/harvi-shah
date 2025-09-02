import os
import requests
import gspread
from google.oauth2.service_account import Credentials
from datetime import date, timedelta

# Config
ACCESS_TOKEN = os.getenv("META_TOKEN")
AD_ACCOUNT_ID = os.getenv("AD_ACCOUNT_ID")  # just the number, not "act_"
SHEET_NAME = os.getenv("SHEET_NAME", "Meta Ads Daily")

# Yesterday’s date
yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")

# Fields to pull
FIELDS = "date_start,campaign_id,campaign_name,adset_id,adset_name,ad_id,ad_name,impressions,clicks,spend,ctr,cpc,cpm,actions"

# Step 1: Call Meta API
url = f"https://graph.facebook.com/v19.0/act_{AD_ACCOUNT_ID}/insights"
params = {
    "fields": FIELDS,
    "level": "campaign",
    "time_increment": "1",
    "time_range": f'{{"since":"{yesterday}","until":"{yesterday}"}}',
    "access_token": ACCESS_TOKEN,
}
resp = requests.get(url, params=params)
resp.raise_for_status()
data = resp.json().get("data", [])

# Step 2: Connect to Google Sheets
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_info(
    json.loads(os.getenv("GOOGLE_CREDENTIALS_JSON")), scopes=scopes
)
gc = gspread.authorize(creds)
sh = gc.open(SHEET_NAME)
worksheet = sh.sheet1

# Step 3: Append rows
rows = []
for d in data:
    rows.append([
        d.get("date_start"),
        d.get("campaign_id"),
        d.get("campaign_name"),
        d.get("adset_id"),
        d.get("adset_name"),
        d.get("ad_id"),
        d.get("ad_name"),
        d.get("impressions"),
        d.get("clicks"),
        d.get("spend"),
        d.get("ctr"),
        d.get("cpc"),
        d.get("cpm"),
        str(d.get("actions")),
    ])
if rows:
    worksheet.append_rows(rows)
