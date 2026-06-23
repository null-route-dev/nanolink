from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())

    click_logs: Mapped[list["ClickLog"]] = relationship(
        back_populates="link", cascade="all, delete-orphan"
    )

class ClickLog(Base):
    __tablename__ = "clicks_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    link_id: Mapped[int] = mapped_column(
        ForeignKey("links.id", ondelete="CASCADE"), nullable=False
    )
    clicked_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    link: Mapped["Link"] = relationship(back_populates="click_logs")