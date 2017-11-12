from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Table, UniqueConstraint, func
from sqlalchemy import ForeignKey, DateTime, create_engine
from sqlalchemy.orm import sessionmaker, relationship, backref
from datetime import datetime
import os

Base = declarative_base()

class Ingredient(Base):
    __tablename__ = 'ingredients'
    __table_args__ = (UniqueConstraint('ingredient', 'recipe_id'),)

    amount = Column(String)
    ingredient = Column(String, primary_key=True)
    notes = Column(String)
    recipe_id = Column(Integer, ForeignKey('recipes.id'), primary_key=True)

    def __init__(self, recipe, amount, ingredient, notes=None):
        self.recipe_id = recipe.id
        self.amount = amount
        self.ingredient = ingredient
        self.notes = notes or ""

    def __repr__(self):
        return "<Ingredient('%s', '%s', '%s', '%s')>" % \
               (self.recipe_id, self.amount, self.ingredient, self.notes)

# store parent/child relationships from recipes table
#recipe_to_recipe = Table('recipe_to_recipe', Base.metadata,
#                         Column('parent_id', Integer, ForeignKey('recipes.id'), primary_key=True),
#                         Column('child_id', Integer, ForeignKey('recipes.id'), primary_key=True),
#                         Column('parent_name', String, ForeignKey('recipes.name'), primary_key=True),
#                         Column('child_name', String, ForeignKey('recipes.name'), primary_key=True)
#                         )

class Recipe(Base):
    __tablename__ = 'recipes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    category= Column(String)
    created = Column(DateTime)
    method = Column(String)
    notes = Column(String)
    source = Column(String)


    #parents_id = Column(Integer, ForeignKey('recipes.id'))
    #subrecipes = relationship("Recipe",
    #                          secondary=recipe_to_recipe,
    #                          primaryjoin="and_(id == recipe_to_recipe.c.parent_id, "
    #                          "name== recipe_to_recipe.c.parent_name)",
    #                          secondaryjoin="and_(id == recipe_to_recipe.c.child_id, "
    #                          "name== recipe_to_recipe.c.child_name)",
    #                          backref='parents'
    #                          )
    ingredients = relationship("Ingredient", backref="recipe")

    def __init__(self, name, category, created=datetime.now(), method=None, notes=None, source=None):
        self.name = name
        self.category = category
        self.created = created
        self.method = method or ""
        self.notes = notes or ""
        self.source = source or ""

    def __repr__(self):
        return "<Recipe('%s', '%s', '%s', '%s')>" % \
               (self.name, self.created, self.notes, self.source)

# store ingredient inventory in pantry table
#pantry = Table('pantry', Base.metadata,
#                         Column('ingredient_id', Integer, primary_key=True,
#                                autoincrement=True),
#                         Column('ingredient_name', String),
#                         Column('category', String),
#                         Column('instock', Boolean),
#                         Column('last_bought', DateTime),
#                         relationship("Ingredient"))


class RecipeManager(object):
    def __init__(self):
        DB_URL = os.environ.get('RECIPE_DB_URL', None)
        self.engine = create_engine(DB_URL)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def lookupRecipe(self, search_term):
        return self.session.query(Recipe.name,
                               Recipe.method).filter(func.lower(Recipe.name).like('%%%s%%'
                                                                      %
                                                                      search_term)).all()

    def listRecipeCategories(self):
        return [i[0] for i in
                self.session.query(Recipe.category).distinct().all()]

    def listRecipes(self, category):
        return [i[0] for i in
                self.session.query(Recipe.name).filter_by(category=category).all()]

    def newIngredient(self, recipe, amount, ingredient_name, notes=None):
        if not notes:
            notes = ""

        ingredient = Ingredient(recipe, amount, ingredient_name, notes)
        self.session.add(ingredient)

        recipe.ingredients.append(ingredient)

        self.commit()
        return ingredient

    def modifyMethod(self, recipe,  text):
        recipe.method = text
        self.commit()
        return recipe

    def addRecipe(self, name, category, method="", notes="", source=""):
        recipe = Recipe(name, category, datetime.now(), method, notes, source)

        self.session.add(recipe)

        self.commit()

        return recipe

    def commit(self):
        self.session.commit()

if __name__=='__main__':
    m = RecipeManager()
    c = m.listRecipeCategories()
    print c
    r = m.listRecipes(c[-1])
    print r
