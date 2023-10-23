import gzip
import shutil
import xml.etree.ElementTree as ET

from db import ExtraJudicialBankruptcyMessage, ObligatoryPayment, MonetaryObligation, Bank, Session, Debtor, Publisher

with gzip.open('ExtrajudicialData.xml.gz', 'rb') as f_in:
    with open('ExtrajudicialBankruptcy_20230808_2.xml', 'wb') as f_out:
        shutil.copyfileobj(f_in, f_out)

tree = ET.parse('ExtrajudicialBankruptcy_20230808_2.xml')
root = tree.getroot()

session = Session()

for xml_message in root.findall('ExtrajudicialBankruptcyMessage'):
    message_id = xml_message.find('Id').text
    number = int(xml_message.find('Number').text)
    type_ = xml_message.find('Type').text
    publish_date = xml_message.find('PublishDate').text
    finish_reason = xml_message.find('FinishReason').text if xml_message.find('FinishReason') is not None else None

    message = ExtraJudicialBankruptcyMessage(
        id=message_id,
        number=number,
        type=type_,
        publish_date=publish_date,
        finish_reason=finish_reason,
    )
    session.add(message)

    debtor = xml_message.find('Debtor')
    debtor_name = debtor.find('Name').text
    debtor_birth_date = debtor.find('BirthDate').text
    debtor_birth_place = debtor.find('BirthPlace').text
    debtor_address = debtor.find('Address').text
    debtor_inn = int(debtor.find('Inn').text) if debtor.find('Inn') is not None else None

    debtor = session.query(Debtor).filter_by(
        name=debtor_name, birth_date=debtor_birth_date, birth_place=debtor_birth_place
    ).first()
    debtor = Debtor(
        name=debtor_name,
        birth_date=debtor_birth_date,
        birth_place=debtor_birth_place,
        inn=debtor_inn
    ) if debtor is None else debtor
    message.debtor = debtor

    publisher = xml_message.find('Publisher')
    publisher_name = publisher.find('Name').text
    publisher_inn = int(publisher.find('Inn').text)
    publisher_ogrn = int(publisher.find('Ogrn').text)

    publisher = session.query(Publisher).filter_by(inn=publisher_inn).first()
    publisher = Publisher(
        name=publisher_name,
        inn=publisher_inn,
        ogrn=publisher_ogrn
    ) if publisher is None else publisher
    message.publisher = publisher

    banks = xml_message.find('Banks')
    if banks is not None:
        for bank in banks.findall('Bank'):
            bank_name = bank.find('Name').text
            bank_bik = int(bank.find('Bik').text) if bank.find('Bik') else None
            bank_obj = session.query(Bank).filter_by(name=bank_name).first()
            if bank_obj is None:
                bank_obj = Bank(
                    name=bank_name,
                    bik=bank_bik,
                )
                session.add(bank_obj)
                session.commit()
            message.banks.append(bank_obj)

    creditors_from_entrepreneurship = xml_message.find('CreditorsFromEntrepreneurship')

    if creditors_from_entrepreneurship is not None:
        monetary_obligations = creditors_from_entrepreneurship.find('MonetaryObligations')
        obligatory_payments = creditors_from_entrepreneurship.find('ObligatoryPayments')
    else:
        monetary_obligations = None
        obligatory_payments = None

    for monetary_obligation in monetary_obligations.findall('MonetaryObligation') if monetary_obligations else []:
        monetary_obligation_creditor_name = monetary_obligation.find('CreditorName').text
        monetary_obligation_content = monetary_obligation.find('Content').text
        monetary_obligation_basis = monetary_obligation.find('Basis').text
        monetary_obligation_total_sum = monetary_obligation.find('TotalSum')
        if monetary_obligation_total_sum is not None:
            monetary_obligation_total_sum = float(monetary_obligation_total_sum.text)

        monetary_obligation_debt_sum = monetary_obligation.find('DebtSum')
        if monetary_obligation_debt_sum is not None:
            monetary_obligation_debt_sum = float(monetary_obligation_debt_sum.text)

        monetary_obligation_obj = MonetaryObligation(
            creditor_name=monetary_obligation_creditor_name,
            content=monetary_obligation_content,
            basis=monetary_obligation_basis,
            total_sum=monetary_obligation_total_sum,
            debt_sum=monetary_obligation_debt_sum,
            message_id=message_id,
            from_entrepreneurship=True,
        )
        session.add(monetary_obligation_obj)
        message.monetary_obligations.append(monetary_obligation_obj)

    for obligatory_payment in obligatory_payments.findall('ObligatoryPayment') if obligatory_payments else []:
        obligatory_payment_name = obligatory_payment.find('Name').text
        obligatory_payment_sum = float(obligatory_payment.find('Sum').text)

        obligatory_payment_obj = ObligatoryPayment(
            name=obligatory_payment_name,
            sum=obligatory_payment_sum,
            message_id=message_id,
            from_entrepreneurship=True
        )
        message.obligatory_payments.append(obligatory_payment_obj)
        session.add(obligatory_payment_obj)

    creditors_non_from_entrepreneurship = xml_message.find('CreditorsNonFromEntrepreneurship')
    if creditors_non_from_entrepreneurship is not None:
        monetary_obligations = creditors_non_from_entrepreneurship.find('MonetaryObligations')
        obligatory_payments = creditors_non_from_entrepreneurship.find('ObligatoryPayments')
    else:
        monetary_obligations = None
        obligatory_payments = None

    for monetary_obligation in monetary_obligations.findall('MonetaryObligation') if monetary_obligations else []:
        monetary_obligation_creditor_name = monetary_obligation.find('CreditorName').text
        monetary_obligation_content = monetary_obligation.find('Content').text
        monetary_obligation_basis = monetary_obligation.find('Basis').text
        monetary_obligation_total_sum = monetary_obligation.find('TotalSum')
        if monetary_obligation_total_sum is not None:
            monetary_obligation_total_sum = float(monetary_obligation_total_sum.text)

        monetary_obligation_debt_sum = monetary_obligation.find('DebtSum')
        if monetary_obligation_debt_sum is not None:
            monetary_obligation_debt_sum = float(monetary_obligation_debt_sum.text)

        monetary_obligation_obj = MonetaryObligation(
            creditor_name=monetary_obligation_creditor_name,
            content=monetary_obligation_content,
            basis=monetary_obligation_basis,
            total_sum=monetary_obligation_total_sum,
            debt_sum=monetary_obligation_debt_sum,
            message_id=message_id,
            from_entrepreneurship=True,
        )
        message.monetary_obligations.append(monetary_obligation_obj)
        session.add(monetary_obligation_obj)

    for obligatory_payment in obligatory_payments.findall('ObligatoryPayment') if obligatory_payments else []:
        obligatory_payment_name = obligatory_payment.find('Name').text
        obligatory_payment_sum = float(obligatory_payment.find('Sum').text)

        obligatory_payment_obj = ObligatoryPayment(
            name=obligatory_payment_name,
            sum=obligatory_payment_sum,
            message_id=message_id,
            from_entrepreneurship=False,
        )
        message.obligatory_payments.append(obligatory_payment_obj)
        session.add(obligatory_payment_obj)

session.commit()
