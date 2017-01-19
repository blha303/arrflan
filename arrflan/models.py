from sqlalchemy import Column, Integer, String
from arrflan.database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    steam_id = Column(String(40))
    nickname = Column(String(80))
    country = Column(String(2))
    state = Column(String(10))
    url = Column(String(17))
    realname = Column(String(140))
    avatar = Column(String(17))

    def __init__(self, steam_id=None, nickname=None):
        self.steam_id = steam_id
        self.nickname = nickname

    def __repr__(self):
        return "<User {} ({})>".format(self.steam_id, self.nickname)
