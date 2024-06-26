from database import Base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, Integer, String, Enum, Float, JSON, Boolean, DateTime, TIMESTAMP
from skin.enums import ESkinExterior, ESkinPhase, ESkinRarity, ESkinType

class Skin(Base):
    __tablename__ = 'skin'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    app_id: Mapped[int] = mapped_column(Integer)
    asset_id: Mapped[int] = mapped_column(Integer)
    collection: Mapped[str | None] = mapped_column(String)
    collection_info: Mapped[dict | None] = mapped_column(JSON)
    price: Mapped[float] = mapped_column(Float)
    float_value: Mapped[float] = mapped_column(Float)

    # Range from 0 to 100
    playside_blue: Mapped[int | None] = mapped_column(Integer)
    fade: Mapped[int | None] = mapped_column(Integer)

    is_souvenir: Mapped[bool] = mapped_column(Boolean)
    is_stattrak: Mapped[bool] = mapped_column(Boolean)
    has_nametag: Mapped[bool] = mapped_column(Boolean)
    
    # Full name also has exterior
    full_name: Mapped[str] = mapped_column(String)
    full_slug: Mapped[str] = mapped_column(String)

    # Short name has no exterior
    short_name: Mapped[str] = mapped_column(String)
    short_slug: Mapped[str] = mapped_column(String)

    # steam akamai image (dont need to parse all)
    img: Mapped[str] = mapped_column(String)
    
    # stickers JSON
    stickers: Mapped[dict] = mapped_column(JSON)

    delivery_time: Mapped[int] = mapped_column(Integer)

    color: Mapped[str] = mapped_column(String)

    rarity: Mapped[str] = mapped_column(String)
    collection: Mapped[str] = mapped_column(String)
    phase: Mapped[ESkinPhase] = mapped_column(Enum(ESkinPhase))
    pattern: Mapped[int] = mapped_column(Integer)

    # Values are enums for convenient filtering
    skin_type: Mapped[ESkinType] = mapped_column(Enum(ESkinType))
    exterior: Mapped[ESkinExterior] = mapped_column(Enum(ESkinExterior))
    rarity: Mapped[ESkinRarity] = mapped_column(Enum(ESkinRarity))

    has_trade_lock: Mapped[bool] = mapped_column(Boolean)
    trade_lock: Mapped[TIMESTAMP] = mapped_column(DateTime)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE")
    )

    user = relationship("User")

    trades = relationship("Trade", back_populates="skins")
    
    