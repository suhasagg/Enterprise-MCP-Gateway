from datetime import datetime
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column
from sqlalchemy import String,DateTime,JSON,Text
class Base(DeclarativeBase): pass
class AuditEvent(Base):
    __tablename__="audit_events"
    id:Mapped[int]=mapped_column(primary_key=True,autoincrement=True)
    request_id:Mapped[str]=mapped_column(String(80),index=True)
    tenant_id:Mapped[str]=mapped_column(String(100),index=True)
    principal:Mapped[str]=mapped_column(String(200))
    tool:Mapped[str]=mapped_column(String(200))
    decision:Mapped[str]=mapped_column(String(30))
    arguments:Mapped[dict]=mapped_column(JSON)
    result_summary:Mapped[str]=mapped_column(Text,default="")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
