from sqlalchemy import Column, Integer, String, DateTime, BigInteger, ForeignKey, Table, Float, create_engine, Boolean, \
    UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(BigInteger, primary_key=True, autoincrement=True)


class Debtor(BaseModel):
    __tablename__ = "debtor"
    __table_args__ = (
        UniqueConstraint('name', 'birth_date', 'birth_place'),
    )

    name = Column(String, nullable=False)
    birth_date = Column(DateTime, nullable=False)
    birth_place = Column(String, nullable=False)
    inn = Column(BigInteger, unique=True, nullable=True)

    address = relationship("Address", back_populates="debtor", uselist=False)
    history_name = relationship("DebtorHistoryName", back_populates="debtor")
    message = relationship('ExtraJudicialBankruptcyMessage', back_populates='debtor')


class Address(BaseModel):
    __tablename__ = "address"

    index = Column(Integer)
    region = Column(String)
    district = Column(String)
    city = Column(String)
    street = Column(String)
    home = Column(Integer)
    apartment = Column(Integer)

    debtor_id = Column(BigInteger, ForeignKey("debtor.id"))
    debtor = relationship("Debtor", back_populates="address")


class DebtorHistoryName(BaseModel):
    __tablename__ = 'debtor_name_history'

    value = Column(String, nullable=False)

    debtor_id = Column(BigInteger, ForeignKey('debtor.id'))
    debtor = relationship('Debtor', back_populates='history_name')


class Publisher(BaseModel):
    __tablename__ = 'publisher'

    name = Column(String, nullable=False)
    inn = Column(BigInteger, nullable=False, unique=True)
    ogrn = Column(BigInteger, nullable=False, unique=True)

    message = relationship('ExtraJudicialBankruptcyMessage', back_populates='publisher')


message__bank = Table(
    "message__bank",
    Base.metadata,
    Column("message_id", ForeignKey("extra_judicial_bankruptcy_message.id")),
    Column("bank_id", ForeignKey("bank.id")),
)


class ExtraJudicialBankruptcyMessage(Base):
    __tablename__ = 'extra_judicial_bankruptcy_message'

    id = Column(String, primary_key=True)
    number = Column(BigInteger, nullable=False)
    type = Column(String, nullable=False)
    publish_date = Column(DateTime, nullable=False)
    finish_reason = Column(String, nullable=True)

    debtor_id = Column(BigInteger, ForeignKey('debtor.id'))
    publisher_id = Column(BigInteger, ForeignKey('publisher.id'))

    publisher = relationship('Publisher', back_populates='message')
    debtor = relationship('Debtor', back_populates='message')
    banks = relationship("Bank", secondary=message__bank, back_populates="messages")
    monetary_obligations = relationship("MonetaryObligation", back_populates="message")
    obligatory_payments = relationship("ObligatoryPayment", back_populates="message")


class Bank(BaseModel):
    __tablename__ = 'bank'

    name = Column(String, nullable=False, unique=True)
    bik = Column(BigInteger, nullable=True)

    messages = relationship("ExtraJudicialBankruptcyMessage", secondary=message__bank, back_populates="banks")


class MonetaryObligation(BaseModel):
    __tablename__ = 'monetary_obligation'

    creditor_name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    basis = Column(String, nullable=False)
    total_sum = Column(Float, nullable=True)
    debt_sum = Column(Float, nullable=True)
    message_id = Column(String, ForeignKey('extra_judicial_bankruptcy_message.id'))
    from_entrepreneurship = Column(Boolean, nullable=False)

    message = relationship("ExtraJudicialBankruptcyMessage", back_populates="monetary_obligations")


class ObligatoryPayment(BaseModel):
    __tablename__ = 'obligatory_payment'

    name = Column(String, nullable=False)
    sum = Column(Float, nullable=True)
    message_id = Column(String, ForeignKey('extra_judicial_bankruptcy_message.id'))
    from_entrepreneurship = Column(Boolean, nullable=False)

    message = relationship("ExtraJudicialBankruptcyMessage", back_populates="obligatory_payments")


engine = create_engine("postgresql+psycopg2://{DB_USER}}:{DB_PASSWORD}}@localhost/{DB_NAME}}")
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
