## [WIP] Telegram bot recipe manager and culinary assistant

### Setup
- Clone this repo
- Install dependencies:
```
cd recipe_manager
pip install -r requirements.txt
```
- Add telegram token and db config in default.env
- Load config:
```
export $(cat default.env | xargs)
```
- Load recipes.csv into db
```
python load_recipes.py
```
- Run bot:
```
python bot.py
```
