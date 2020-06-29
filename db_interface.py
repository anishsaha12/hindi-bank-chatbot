from pymongo import MongoClient
import pprint
import datetime
import random
from bson.objectid import ObjectId
import smtplib


# connect to mongodb client
client = MongoClient("mongodb+srv://chatbot:chatbot@hibot-9tr4x.gcp.mongodb.net/<dbname>?retryWrites=true&w=majority")


# assign collections
chatbot = client.bankDatabase.bankingRecords
chatbotDetails = client.bankDatabase.bankDetails




# send otp to email id and to the database, then when user enters the otp from email, it can be verified from database
def send_otp(mob_no, email):
    find_details = {"person.mobile_no": mob_no, "person.email_id": email}
    
    
    server = smtplib.SMTP('smtp.gmail.com', 587) 
    server.starttls() 
    server.login("sender_email", "sender_email_password") 
    subject = "OTP Verification"
    otp = random.randrange(10000, 99999)
    message = message = 'Subject: {}\n\n{}'.format(subject, otp)
    server.sendmail("sender_email", email, message) 
    server.quit() 
    
    set_otp = {
        '$set': {
            "person.otp": otp
        }
    }
    chatbot.update_one(find_details, set_otp)
    return True
    


def account_balance(acc_bal_values):
    '''
    # account balance - account number, mobile no, otp = returns account balance of savings account only
    acc_bal_values = [128890, 9988776655, 9999]
    '''
    
    acc_no = acc_bal_values[0]
    mob_no = acc_bal_values[1]
    otp = acc_bal_values[2]
    
    acc_bal_query = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "person.otp": otp}
    acc_project = {"_id": 0, "accounts.savings.balance": 1}
    
    acc_bal = chatbot.find(acc_bal_query, acc_project)
    balance = acc_bal[0]['accounts']['savings']['balance']
    
    return balance




def payment(payment_values):
    '''
    # payment - account no, receiver's account number, receiver's IFSC code, amount, mobile no, otp = deduct balance, write into transactions
    payment_values = [128890, 159159, 'YYY12312312', 500, 9988776655, 9999]
    '''
    
    acc_no = payment_values[0]
    rec_acc_no = payment_values[1]
    rec_ifsc = payment_values[2]
    amt = payment_values[3]
    mob_no = payment_values[4]
    otp = payment_values[5]

    acc_bal_query = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "person.otp": otp}
    acc_project = {"_id": 0, "accounts.savings.balance": 1}
    
    acc_bal = chatbot.find(acc_bal_query, acc_project)
    balance = acc_bal[0]['accounts']['savings']['balance']
    
    date = datetime.datetime.now()

    paymt = {
        "$push": {
            "transactions": {
                "amount": amt,
                "account_number": rec_acc_no,
                "date": str(date.day)+"-"+str(date.month)+"-"+str(date.year) 
            }
        }
    }

    new_balance = balance - amt
    
    if new_balance > 0:
        update_balance = {
            "$set": {
                "accounts.savings.balance": new_balance
            }
        }
        chatbot.update_one(acc_bal_query, update_balance)
        chatbot.update_one(acc_bal_query, paymt)
        return True
    else:
        return False




def account_registration(registration_values):
    '''
    # registration to open account - account type, fname, lname, mobile no, email, pan, aadhar, line1, line2, city, state, zip, country  = add new data
    registration_values = ["savings", "mnzxccx", "asdds", 9632145871, "dhee@gmail.com", "asd123233", "147526589874", "Bengaluru"]
    '''
    
    account_type = registration_values[0]
    fname = registration_values[1]
    lname = registration_values[2]
    mobile_no = registration_values[3]
    email = registration_values[4]
    pan = registration_values[5]
    aadhar = registration_values[6]
    address = registration_values[7]
    
    cif_no = random.randrange(100000000000, 999999999999)
    cif_no_encode = str(cif_no).encode()
    cif_no_encode = ObjectId(cif_no_encode)

    register_acc = {
        "_id": {
            "oid": cif_no_encode
        },
    
        "person": {
            "fname": fname,
            "lname": lname,
            "address": address,
            "cif_no": cif_no,
            "mobile_no": mobile_no,
            "email_id": email,
            "pan_no": pan,
            "aadhar_no": aadhar ,
            "otp": 9999
        },
    
        "accounts": {
            "savings": {
                "balance": 0,
                "number": random.randrange(100000, 999999),
                "cards": {
                    "debit_card": {
                        "no": random.randrange(1000000000000000, 9999999999999999),
                        "status": "blocked",
                        "expiry":"12-22",
                        "pin": random.randrange(1000, 9999)
                    }
                },
                "cheque_book": {
                    "issued": "no"
                },
                "net_banking": {
                    "password": "qwertyuiop"
                }
            }
        },
    
        "branch": {
            "location": "malleshwaram",
            "city": "Bengaluru",
            "state": "Karnataka",
            "ifsc_code": "XXX45233244",
            "branch_code": 45233244,
            "phone": 1122334455,
            "hours": "10AM–5PM"
        }
    }

    if(chatbot.insert_one(register_acc)):
        res = "खाता पंजीकरण सफल हो गया|"
        return True
    else:
        res = "खाता पंजीकरण असफल। बाद में पुन: प्रयास करें|"
        return False




def add_beneficiary(beneficiary_values):
    '''
    # add beneficiary - account no, mobile no, otp, beneficiary's IFSC code, bank name = add beneficiary
    beneficiary_values = [128890, 9988776655, 9999, 'YYY45233244', 'Citi']
    '''
    
    account_no = beneficiary_values[0]
    mobile_no = beneficiary_values[1]
    otp = beneficiary_values[2]
    ben_ifsc = beneficiary_values[3]
    bank_name = beneficiary_values[4]

    find_person = {"person.mobile_no": mobile_no, "person.otp": otp}

    add_ben = {
        '$push': {
            "beneficiary":{
                "ifsc_code": ben_ifsc,
                "bank": bank_name
            }
        }
    }

    if(chatbot.update_one(find_person, add_ben)):
        res = "लाभार्थी को सफलता पूर्वक जोड़ा गया|"
        return True
    else:
        res = "लाभार्थी जोड़ना असफल हुवा| बाद में पुन: प्रयास करें|"
        return False




def view_transactions(transaction_values):
    '''
    # view transactions - account no, mobile no, otp = show recent 5 transactions
    transaction_values = [128890, 9988776655, 9999]
    '''
    
    acc_no = transaction_values[0]
    mob_no = transaction_values[1]
    otp = transaction_values[2]

    view_trans_query = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "person.otp": otp}
    trans_project = {"_id": 0, "transactions": 1}
    
    trans = chatbot.find(view_trans_query, trans_project)
    trans = trans[0]['transactions'][-10:]
    
    res = []
    
    for trx in trans:
        tmp = []
        for k,v in trx.items():
            tmp.append(k+': '+str(v))
        res.append('\n'.join(tmp))
        
    return '\n\n'.join(res)



def branch_info(branch_info_values):
    '''# branch information - city name
    branch_info_values = ['Bengaluru']
    '''
    
    city = branch_info_values[0]

    branch_info_query = {"city": city}
    branch_info_project = {"location":1, "phone":1, "hours":1}

    branch_info = chatbotDetails.find(branch_info_query, branch_info_project)
    
    res = []
    for i,branches in enumerate(branch_info):
        res.append(str(i+1)+'. Location: '+str(branches['location']) + " - Ph.no.: " + str(branches['phone']) + 
                   " - Hours: " + str(branches['hours']))

    return '\n'.join(res)



def block_card(block_card_values):
    '''
    # block card - option (block, freeze), account no, mobile no, card no, otp = change status
    block_card_values = ['credit_card', 'blocked', 128890, 9988776655, 4561123475341596, 9999]
    '''
    
    card = block_card_values[0]
    option = block_card_values[1]
    acc_no = block_card_values[2]
    mob_no = block_card_values[3]
    card_no = block_card_values[4]
    otp = block_card_values[5]

    set_credit_card = {
        '$set': {
            "accounts.savings.cards.credit_card.status": option
        }
    }

    set_debit_card = {
        '$set': {
            "accounts.savings.cards.debit_card.status": option
        }
    }


    if card == 'credit_card':    
        find_card = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "person.otp": otp,
                     "accounts.savings.cards.credit_card.no": card_no}
        chatbot.update_one(find_card, set_credit_card)
        res = "आपका कार्ड सफलता पूर्वक "+ str(option) + "किया गया है|"
        return True

    if card == 'debit_card':  
        find_card = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "person.otp": otp,
                     "accounts.savings.cards.debit_card.no": card_no}
        if (chatbot.update_one(find_card, set_debit_card)):
            res = "आपका कार्ड सफलता पूर्वक "+ str(option) + "किया गया है|"
            return True
        else:
            return False
        
    
    else:
        res = "आपका कार्ड " + str(option) + "असफल हुवा| बाद में पुन: प्रयास करें|"
        return False




def forgot_pass_net(forgot_pass_net_values):
    '''# forgot password net banking - account no, home branch code, cif no, otp = link to change password
    forgot_pass_net_values = [128890, 45233244, 123456789123, 9999]
    '''
    
    acc_no = forgot_pass_net_values[0]
    branch_code = forgot_pass_net_values[1]
    cif_no =forgot_pass_net_values[2]
    otp = forgot_pass_net_values[3]


    find_details = {"accounts.savings.number": acc_no, "person.cif_no": cif_no, "person.otp": otp, "branch.branch_code": branch_code}

    if(chatbot.find(find_details)):
        res = "पासवर्ड बदलने के लिए लिंक: www./.../"
        return True
    else:
        res = "क्रेडेंशियल पुनर्प्राप्ति असफल हुवा| बाद में पुन: प्रयास करें|"
        return False



def forgot_pass_atm(forgot_pass_atm):
    '''# forgot password atm - account no, mobile no, card no, expiry date, fname, lname, otp, new pin =  update
    forgot_pass_atm = [128890, 9988776655, 4561123475341596, '12-20', 'kriishna', 'kumar', 9999, 4455]
    '''

    acc_no = forgot_pass_atm[0]
    mob_no = forgot_pass_atm[1]
    card_no = forgot_pass_atm[2]
    exp_date = forgot_pass_atm[3]
    fname = forgot_pass_atm[4]
    lname = forgot_pass_atm[5]
    otp = forgot_pass_atm[6]
    new_pin = forgot_pass_atm[7]

    find_details = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "person.otp": otp, 
                    "accounts.savings.debit_card.no": card_no, "accounts.savings.debit_card.expiry": exp_date}

    if(chatbot.find(find_details)):
        set_pin = {
            '$set': {
                "accounts.savings.cards.debit_card.pin": new_pin
            }
        }
    
        if(chatbot.update_one(find_card, set_pin)):
            res = "ATM पिन सफलता पूर्वक बदल गया"
            return True
        else:
            res = "पिन परिवर्तन अनुरोध विफल रहा| बाद में पुन: प्रयास करें|"
            return False




def reset_pass_net(reset_pass_net_values):
    '''# reset password net banking - account no, home branch code, mobile no, otp, present password two times = link to update password
    reset_pass_net_values = [128890, 45233244, 9988776655,  9999, 'qwertyuiop', 'qwertyuiop']
    '''
    
    acc_no = reset_pass_net_values[0]
    branch_code = reset_pass_net_values[1]
    mob_no =reset_pass_net_values[2]
    otp = reset_pass_net_values[3]
    pass1 = reset_pass_net_values[4]
    pass2 = reset_pass_net_values[5]

    if pass1 == pass2:
        find_details = {"accounts.savings.net_banking.password": pass1, "accounts.savings.number": acc_no, "person.mobile_no": mob_no, "person.otp": otp, "branch.branch_code": branch_code}
    else:
        return False
    
    if(chatbot.find(find_details).count() != 0):
        res = "पासवर्ड बदलने के लिए लिंक: www./.../"
        return True
    else:
        res = "क्रेडेंशियल पुनर्प्राप्ति असफल हुवा| बाद में पुन: प्रयास करें|"
        return False




def credit_card_balance(credit_bal_values):
    '''# credit card balance details - mobile no, otp = credit card no and balance
    credit_bal_values = [9988776655, 9999]
    '''
    
    mob_no = credit_bal_values[0]
    otp = credit_bal_values[1]

    bal_query = {"person.mobile_no": mob_no, "person.otp": otp}
    bal_project = {"_id":0, "accounts.savings.cards.credit_card.balance": 1}

    credit_bal = chatbot.find(bal_query, bal_project)
    balance = credit_bal[0]['accounts']['savings']['cards']['credit_card']['balance']
    
    return balance




def credit_card_status(credit_stat_values):
    '''# credit card status - mobile no, otp = status 
    credit_stat_values = [9988776655, 9999]
    '''
    
    mob_no = credit_stat_values[0]
    otp = credit_stat_values[1]

    stat_query = {"person.mobile_no": mob_no, "person.otp": otp}
    stat_project = {"_id":0, "accounts.savings.cards.credit_card.status": 1}

    credit_stat = chatbot.find(stat_query, stat_project)
    status = credit_stat[0]['accounts']['savings']['cards']['credit_card']['status']
    
    return status




def credit_card_invoice(credit_trans_values):
    '''# credit card invoice - mobile no, otp = invoice
    credit_trans_values = [9988776655, 9999]
    '''
    
    mob_no = credit_trans_values[0]
    otp = credit_trans_values[1]

    trans_query = {"person.mobile_no": mob_no, "person.otp": otp}
    trans_project = {"_id":0, "accounts.savings.cards.credit_card.transactions": 1}

    cred_trans = chatbot.find(trans_query, trans_project)
    credit_trans = cred_trans[0]['accounts']['savings']['cards']['credit_card']['transactions']
    return str(credit_trans)




def credit_card_limit(credit_limit_values):
    '''# credit card limit - mobile no, otp = show monthly limit
    credit_limit_values = [9988776655, 9999]
    '''
    
    mob_no = credit_limit_values[0]
    otp = credit_limit_values[1]

    limit_query = {"person.mobile_no": mob_no, "person.otp": otp}
    limit_project = {"_id":0, "accounts.savings.cards.credit_card.monthly_limit": 1}

    credit_limit = chatbot.find(limit_query, limit_project)
    limit = credit_limit[0]['accounts']['savings']['cards']['credit_card']['monthly_limit']
    
    return limit




def issue_cheque_book(iss_cheq_values):
    '''# issue cheque book - account no, mobile no, otp
    iss_cheq_values = [128890, 9988776655, 9999]
    '''
    
    acc_no = iss_cheq_values[0]
    mob_no = iss_cheq_values[1]
    otp = iss_cheq_values[2]

    cheq_query = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "person.otp": otp}
    cheq_project = {"_id":0, "accounts.savings.cheque_book": 1}

    cheq = chatbot.find(cheq_query, cheq_project)
    cheque_issue = cheq[0]['accounts']['savings']['cheque_book']

    if(cheque_issue['issued']=='yes'):
        return False
    else:
        cheq_no = random.randrange(1000000000, 9999999999)
    
        issue_new_cheq = {
            '$push': {
                "accounts.savings.cheque_book.cheques": {
                    "no": cheq_no
                }
            }
        }
    
        set_issued_yes = {
            '$set': {
                "accounts.savings.cheque_book.issued": "yes"
            }
        }
    
        if(chatbot.update_one(cheq_query, set_issued_yes) and chatbot.update_one(cheq_query, issue_new_cheq)):
            res = "नई चेक बुक, नंबर " + str(cheq_no) + " जारी कर दिया गया है"
            return cheq_no
        else:
            return False




def auth_acc(acc_no):
    check = {"accounts.savings.number": acc_no}
    
    if(chatbot.find(check).count() == 0):
        res = "खाता संख्या गलत है| कृपया सही खाता संख्या फिरसे लिखिए|"
        return False
    else:
        return True




def auth_mob(acc_no, mob_no):
    check = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no}
    
    if(chatbot.find(check).count() == 0):
        res = "मोबाइल नंबर गलत है| कृपया सही मोबाइल नंबर फिरसे लिखिए|"
        return False
    else: 
        return True




def auth_otp(acc_no, mob_no, otp):
    check = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "person.otp": otp}
    
    if(chatbot.find(check).count() == 0):
        res = "OTP गलत है| कृपया सही OTP फिरसे लिखिए|"
        return False
    else:
        return True




def auth_ifsc(acc_no, ifsc_no):
    check = {"accounts.savings.number": acc_no, "branch.ifsc_code": ifsc_no}
    
    if(chatbot.find(check).count() == 0):
        res =  "आई.एफ.एस.इ संख्या गलत है| कृपया सही आई.एफ.एस.इ संख्या फिरसे लिखिए|"
        return False
    else:
        return True




def auth_cif(acc_no, cif_no):
    check = {"accounts.savings.number": acc_no, "person.cif_no": cif_no}
    
    if(chatbot.find(check).count() == 0):
        res = "सि.आई.एफ संख्या गलत है| कृपया सही सि.आई.एफ संख्या फिरसे लिखिए|"
        return False
    else:
        return True




def auth_branch(acc_no, branch_code):
    check = {"accounts.savings.number": acc_no, "branch.branch_code": branch_code}
    
    if(chatbot.find(check).count() == 0):
        res = "आपके home बैंक का ब्रांच कोड गलत है| कृपया सही ब्रांच कोड फिरसे लिखिए|"
        return False
    else:
        return True




def auth_credit(acc_no, mob_no, card_no):
    check = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "accounts.savings.cards.credit_card.no": card_no}
    
    if(chatbot.find(check).count() == 0):
        res = "क्रेडिट कार्ड संख्या गलत है| कृपया सही क्रेडिट कार्ड संख्या फिरसे लिखिए|"
        return False
    else:
        return True




def auth_debit(acc_no, mob_no, card_no):
    check = {"accounts.savings.number": acc_no, "person.mobile_no": mob_no, "accounts.savings.cards.debit_card.no": card_no}
    
    if(chatbot.find(check).count() == 0):
        res =  "डेबिट कार्ड संख्या गलत है| कृपया सही डेबिट कार्ड संख्या फिरसे लिखिए|"
        return False
    else:
        return True




def auth_credit_card_expiry(card_no, exp_date):
    check = {"accounts.savings.cards.credit_card.no": card_no, "accounts.savings.cards.credit_card.expiry": exp_date}
    
    if(chatbot.find(check).count() == 0):
        res = "आपका क्रेडिट कार्ड expiry गलत है| कृपया सही क्रेडिट कार्ड expiry फिरसे लिखिए|"
        return False
    else:
        return True




def auth_debit_card_expiry(card_no, exp_date):
    check = {"accounts.savings.cards.debit_card.no": card_no, "accounts.savings.cards.debit_card.expiry": exp_date}
    
    if(chatbot.find(check).count() == 0):
        res = "आपका डेबिट कार्ड expiry गलत है| कृपया सही डेबिट कार्ड expiry फिरसे लिखिए|"
        return False
    else:
        return True

