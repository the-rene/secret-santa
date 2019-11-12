from random import shuffle
from smtplib import SMTP_SSL, SMTPException
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


TEST_FLAG = False
SMTP_HOST = "smtp.example.org"
SMTP_PORT = 465  # using ssl here
MAIL_USER = "sender-mail@example.org"
MAIL_PASS = "secret"


class Participant:
    def __init__(self, name, mail_address, partner=None):
        self.name = name
        self.mail_address = mail_address
        self.partner = partner

    def mail(self, subject, message, sender):
        if (TEST_FLAG):
            self.mail_test(subject, message, sender)
        else:
            self.mail_prod(subject, message, sender)

    def mail_test(self, subject, message, sender):
        print('Would have sent mail to {} from {} with subject "{}" and this content:'.format(self.mail_address,sender,subject))
        print(message)

    def mail_prod(self, subject, message, sender):

        send_mail(
            subject=subject,
            message=message,
            from_email=sender,
            recipient_email=self.mail_address
        )

    def set_partner(self, partner):
        self.partner = partner
        partner.partner =self

    def __str__(self):
        return self.name


def send_mail(subject, message, from_email, recipient_email):
    msg = MIMEMultipart()

    msg['From'] = from_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    try:
        with SMTP_SSL(host=SMTP_HOST, port=SMTP_PORT) as smtp:
            smtp.set_debuglevel(False)
            smtp.ehlo()
            smtp.login(MAIL_USER,MAIL_PASS)
            smtp.sendmail(MAIL_USER,recipient_email,msg.as_string())
            smtp.quit()
    except SMTPException as e:
        print(e)


def get_participants():
    """
    Example data with two times two participants who are partners and shall not gift each other and two participants
    with no partner also participating. This method should be replaced by your own particpant list, possibly generated
    from a database or ldap server or whatsoever.
    :return: list of all particpants
    """
    first = Participant("first name", "first@example.org")
    second = Participant("second name", "second@example.org")
    # first participant is parnter of second. (this will avoid, that those are gifting each other)
    first.set_partner(second)
    third = Participant("third name", "third@example.org")
    fourth = Participant("fourth name", "fourth@example.org")
    third.set_partner(fourth)
    fifth = Participant("fifth name", "fifth@example.org")
    sixth = Participant("sixth name", "sixth@example.org")
    participants = [first, second, third, fourth, fifth, fifth]
    return participants


def secret_santa_magic(participants):
    print('"Magic!"')
    flag = True
    runs = 1
    while flag:
        flag = False
        shuffle(participants)
        previous = participants[-1]
        for t in participants:
            schenker = previous
            beschenkter = t
            if beschenkter == schenker.partner:
                flag = True
                runs += 1
                break
            else:
                previous = beschenkter
    print("After {} attempts successfully performed magic!".format(runs))
    return participants


def secret_santabot():
    if (yes_or_no(
            'Would you like the Secret Santabot to assign a person to gift to all participants?\n'
            'He will send a mail to each participant')):
        print("Alright, starting!")
    else:
        print("Alright then, bye.")
        return 0

    # do the magic! Will shuffle the particpants
    participants = secret_santa_magic(get_participants())

    for particpant in participants:
        if particpant.mail_address is None or particpant.mail_address == '':
            print(particpant.name + " has no email address. Santabot must quit now.")
            return 1

    # save first: participant
    first = participants[0]
    # each participant gifts the next one in the shuffled list. the last one gifts the first one.
    # thus 'previous' is the last one in the beginning
    previous = participants[-1]

    for particpant in participants:
        donor = previous
        donee = particpant

        # geheim! print(schenker.name+" beschenkt "+beschenkter.name)
        message = 'Hello {}!\r\nAt this years Secret Santa you give a present to {}.\r\n\r\nBest Regards\r\nYour Secret Santabot'.format(
            donor, donee)
        donor.mail("Secret Santa 2019 (TOP SECRET)", message, "secret-santa@example.org")

        previous = donee

    print("Sucess!")
    return 0


def yes_or_no(question):
    while "Invalid answer":
        reply = str(input(question + ' (y/n): ')).lower().strip()
        if reply[0] == 'y':
            return True
        if reply[0] == 'n':
            return False


if __name__ == '__main__':
    secret_santabot()
