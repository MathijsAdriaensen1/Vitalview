from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Float, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

# ✅ Auth0 User met extra profielinfo
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True)  # Auth0 ID
    email = Column(String, unique=True)
    name = Column(String)
    voornaam = Column(String)
    achternaam = Column(String)
    telefoonnummer = Column(String)
    profiel_foto = Column(String, default="img/default.png")
    darkmode = Column(Boolean, default=False)
    taal = Column(String, default="nl")

    gezondheid_data = relationship("GezondheidData", back_populates="gebruiker", cascade="all, delete-orphan")
    contactberichten = relationship("ContactBericht", back_populates="gebruiker", cascade="all, delete-orphan")


# 📊 Gezondheidsdata
class GezondheidData(Base):
    __tablename__ = "gezondheid_data"
    id = Column(Integer, primary_key=True)
    gebruiker_id = Column(Integer, ForeignKey("users.id"))
    datum = Column(DateTime, default=datetime.utcnow)
    categorie = Column(String)  # Gewicht, hartslag, bloeddruk, activiteit,...
    waarde = Column(Float)
    eenheid = Column(String)  # kg, bpm, mmHg, stappen...

    gebruiker = relationship("User", back_populates="gezondheid_data")


# 📨 Contactberichten van gebruikers
class ContactBericht(Base):
    __tablename__ = "contact_berichten"
    id = Column(Integer, primary_key=True)
    gebruiker_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    naam = Column(String, nullable=False)
    email = Column(String, nullable=False)
    telefoon = Column(String)
    onderwerp = Column(String, nullable=False)
    bericht = Column(String, nullable=False)
    datum = Column(DateTime, default=datetime.utcnow)

    gebruiker = relationship("User", back_populates="contactberichten")


# ✅ Admin exportlog (voor PDF/CSV's)
class ExportLog(Base):
    __tablename__ = "export_logs"
    id = Column(Integer, primary_key=True)
    admin_email = Column(String)
    filter_info = Column(String)
    bestandstype = Column(String)  # PDF of CSV
    tijdstip = Column(DateTime, default=datetime.utcnow)