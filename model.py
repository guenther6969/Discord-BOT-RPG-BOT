from peewee import *

# Define o nome do banco de dados
db = SqliteDatabase('monki.db')

# Cria um modelo base de classe, importando o model do peewee
class BaseModel(Model):
    class Meta:
        database = db

# Cria a classe Attack, com seus respectivos campos e formatos (Formatos esse do peewee)
# que é convertida para uma tabela pelo peewee
class Attack(BaseModel):
    username = CharField()
    name = CharField(unique=True)
    attack = TextField()

# Criar tabelas    
if __name__ == '__main__':
    try:
        BaseModel.create_table()
        Attack.create_table()
        print("Tabelas criadas com sucesso!")
    except OperationalError:
        print("Tabela ja existe!")
        
    
    
