import copy

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

import models.db_models as m

class Creator:
    def __init__(self, session: AsyncSession):
        self.session = session



