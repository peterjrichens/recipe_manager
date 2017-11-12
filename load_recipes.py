from recipe_manager import RecipeManager
import pandas as pd


recipes = pd.read_csv('recipes.csv')
m = RecipeManager()
for recipe in recipes.iterrows():
    recipe_name = recipe[1]['Dish']
    category = recipe[1]['Category']
    r = m.addRecipe(recipe_name, category)
    method_text = recipe[1]['Method']
    r = m.modifyMethod(r, method_text)
    if type(recipe[1]['Requires']) == type('string'):
        ingredients = [i for i in recipe[1]['Requires'].split(";") if i!='']
        for i in ingredients:
            ingredient = m.newIngredient(r,'',i,'')
#r.subrecipes.append(r2)
m.commit()
print r.name, r.ingredients
