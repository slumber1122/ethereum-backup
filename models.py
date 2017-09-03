from peewee import *


class BaseModel(Model):
    class Meta:
        db = db

class Block(BaseModel):
    number = CharField()
    blockhash = CharField()
