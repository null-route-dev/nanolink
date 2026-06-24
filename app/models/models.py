from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    links: Mapped[list["Link"]] = relationship(
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    clicks: Mapped[list["ClickLog"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"

class Link(Base):
    __tablename__ = "links"

    id: Mapped[int] = mapped_column(primary_key=True)
    short_code: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    user: Mapped["User | None"] = relationship(back_populates="links")
    click_logs: Mapped[list["ClickLog"]] = relationship(
        back_populates="link", 
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<Link(id={self.id}, short_code={self.short_code}, user_id={self.user_id})>"

class ClickLog(Base):
    __tablename__ = "clicks_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    link_id: Mapped[int] = mapped_column(
        ForeignKey("links.id", ondelete="CASCADE"), 
        nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    clicked_at: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)

    link: Mapped["Link"] = relationship(back_populates="click_logs")
    user: Mapped["User | None"] = relationship(back_populates="clicks")
    
    def __repr__(self):
        return f"<ClickLog(id={self.id}, link_id={self.link_id}, user_id={self.user_id}, clicked_at={self.clicked_at})>"