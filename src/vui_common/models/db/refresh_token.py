from sqlalchemy import Column, String, ForeignKey, DateTime as DateTimeA, func

from vui_common.security.schemas.guid import GUID
from vui_common.database.base import Base


class RefreshToken(Base):
    __tablename__ = 'tokens'
    token = Column(String(36),
                   nullable=False,
                   primary_key=True,
                   unique=True)
    user_id = Column(GUID(),
                     ForeignKey('users.id'),
                     nullable=False)
    time_created = Column(DateTimeA(timezone=True), server_default=func.now())
    time_updated = Column(DateTimeA(timezone=True), onupdate=func.now())

    def toJSON(self):
        return {'token': self.token,
                'user_id': self.user_id
                }
