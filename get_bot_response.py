import xml.etree.ElementTree as ET
import pickle, string
import random
import json
from class_def import Transition, State
from get_class import get_txt_class
import db_interface as db
from nerTagger import *
              


def find_state_by_id(complete_fst_with_words_state_list,id):
    for idx,state in enumerate(complete_fst_with_words_state_list):
        if state.id == id:
            return idx
    return None

def preprocess_text(sentence):
    sentence = sentence.translate(str.maketrans('', '', string.punctuation))        # remove punct
    sentence = sentence.replace('।','')                                             # remove punct
    sentence = sentence.replace('|','')                                             # remove punct
    sentence = sentence.strip()                                                     # remove punct
    sentence = sentence.replace('  ',' ')                                           # remove extra space
    sentence = sentence.replace('है','')                                             # remove stop word
    sentence = sentence.lower()                                                     # lower case
    return sentence

## first display greetings
## display a list of all supported categories
## determine category from user input using sentence classifier

## checked for: account_balance- , payment- , forgot_password-Net Banking, lost_debit_card-Block Card ,
##              registration_to_open_account-Savings Account , view_transactions- , branch_information-City , 
##              add_beneficiary- , credit_card_details-Limit , issue_check_book- , reset_password-Net Banking
## doesnt work for: 

full_fst_states_list = None
init_state = None

def init(main_cat='account_balance-'):
    global full_fst_states_list
    global init_state
    
    with open('./data/data_cat_fst/'+main_cat+'/'+'full_fst_states_list.pkl', 'rb') as f:
            full_fst_states_list = pickle.load(f)

    init_state = None
    for state in full_fst_states_list:
        if state.category=='init':
            init_state = state

# current = init_state
current = None
cat = None
expand_current = None
states_list = None
need_input = None
got_inputs = dict()

def get_expanded_txt():
    global expand_current
    global states_list
    while True:
        try:
            expand_current = states_list[
                find_state_by_id(states_list,
                                 expand_current.out_tr[random.randint(0, len(expand_current.out_tr)-1)].next_state_id)
                                        ]
        except:
            return ''
        if (expand_current.prompt!=''):
            return expand_current.prompt

def talk(inp_txt=None):
    global cat
    global need_input
    global current
    global expand_current
    global states_list
    global got_inputs
    
    if (current is None) or (current.category=='final'):
        cat=None
        need_input=None
        current=None
        expand_current=None
        states_list=None
        got_inputs=dict()
        if inp_txt is None:
            return 'इस सेवा का उपयोग करने के लिए शुक्रिया। आपकी क्या सहायता कर सकता हु?'
        else:
            ## use sentence classifier to obtain category from inp_txt and the do: init(category)
            try:
                find = preprocess_text(inp_txt)
                category, result = get_txt_class(find)
                init(category)
                current = init_state
                return talk()
            except:
                return 'माफ़ करें। यह ऑपरेशन अभी तक हमारे द्वारा समर्थित नहीं है।'
                 
        
    if (current is not None) and (current==init_state):
        ## ignore all states like client input for help or greetings.
        ## traverse upto first authentication state
        while True:
            current = full_fst_states_list[find_state_by_id(full_fst_states_list,
                                                            current.out_tr[0].next_state_id)
                                          ]
            if (current.state_type=='expand') and (not current.category.startswith('greeting')):
                break
    
    if cat is None:
        cat = current.category+'-'+current.sub_category.replace(':','')
        with open('./data/data_cat_fst/'+cat+'/'+'full_fst_states_list.pkl', 'rb') as f:
            states_list = pickle.load(f)

        expand_init = None
        for state in states_list:
            if state.category=='init':
                expand_init = state

        expand_current = expand_init
        prompt = get_expanded_txt()
        
        need_input = current.sub_category

        if current.category=="goodbye":
            cat=None
            need_input=None
            current=None
            expand_current=None
            states_list=None
            got_inputs=dict()
            prompt = prompt+ 'आपकी और क्या सहायता कर सकता हु?'
        
        elif (current.category=="confirmation_by_customer") or (current.category=="rejection_by_customer"):
            return talk()

        return prompt
    else:
        ## process inp_txt
        ## according to need_input
        ## ...
        if need_input in ['Account Number','Mobile Number','OTP','input_data','Debit Card Number','Debit Card Expiry',
                          'Debit Card Holder Name','CIF Number','Home Bank','Mobile Number Link','OTP Link','Location']:
            if inp_txt is None:
                return 'क्षमा करें, आपको समझ नहीं सका। कृपया सही '+need_input+' बताएं।'
            else:
                ## do ner tagging and extract required value from inp_text
                value = inp_txt
                
                if need_input=='Account Number':   # authenticate
                    value = nerTagger(inp_txt)
                    extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                    value = extract_value[0]
                    if db.auth_acc(int(value)):
                        got_inputs['Account Number'] = int(value)
                        pass
                    else:
                        return "खाता संख्या गलत है| कृपया सही खाता संख्या फिरसे लिखिए|"
                
                elif need_input=='Mobile Number':   # authenticate
                    value = nerTagger(inp_txt)
                    extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                    value = extract_value[0]
                    if db.auth_mob(got_inputs['Account Number'], int(value)):
                        got_inputs['Mobile Number'] = int(value)
                        pass
                    else:
                        return "मोबाइल नंबर गलत है| कृपया सही मोबाइल नंबर फिरसे लिखिए|"
                
                elif need_input=='OTP':   # authenticate
                    value = nerTagger(inp_txt)
                    extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                    value = extract_value[0]
                    if db.auth_otp(got_inputs['Account Number'],got_inputs['Mobile Number'],int(value)):
                        got_inputs['OTP'] = int(value)
                        pass
                    else:
                        return "OTP गलत है| कृपया सही OTP फिरसे लिखिए|"
                
                elif (need_input=='input_data') and (current.category == 'payment'):   # other inputs
                    if got_inputs.get('receiver_acc',None) is None:    ## didn't still get receiver_acc
                        value = nerTagger(inp_txt)
                        extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                        value = extract_value[0]
                        got_inputs['receiver_acc'] = int(value)
                        pass
                    elif got_inputs.get('receiver_IFSC',None) is None:    ## didn't still get receiver_IFSC
                        got_inputs['receiver_IFSC'] = value
                        pass
                    elif got_inputs.get('receiver_amt',None) is None:    ## didn't still get receiver_amt
                        value = nerTagger(inp_txt)
                        extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                        value = extract_value[0]
                        got_inputs['receiver_amt'] = int(value)
                        pass
                    
                elif need_input=='CIF Number':   # get data
                    value = nerTagger(inp_txt)
                    extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                    value = extract_value[0]
                    if db.auth_cif(got_inputs['Account Number'],int(value)):
                        got_inputs['CIF Number'] = int(value)
                        pass
                    else:
                        return "सि.आई.एफ संख्या गलत है| कृपया सही सि.आई.एफ संख्या फिरसे लिखिए|"
                    
                elif need_input=='Home Bank':   # get data
                    value = nerTagger(inp_txt)
                    extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                    value = extract_value[0]
                    if db.auth_branch(got_inputs['Account Number'],int(value)):
                        got_inputs['Home Bank'] = int(value)
                        pass
                    else:
                        return "आपके home बैंक का ब्रांच कोड गलत है| कृपया सही ब्रांच कोड फिरसे लिखिए|"
                    
                elif (need_input=='input_data') and (current.category == 'lost_debit_card'):   # other inputs
                    value = nerTagger(inp_txt)
                    extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                    value = extract_value[0]
                    if got_inputs.get('debit_card_num',None) is None:    ## didn't still get debit_card_num
                        got_inputs['debit_card_num'] = int(value)
                        pass
                    
                elif need_input=='Mobile Number Link':   # get data
                    value = nerTagger(inp_txt)
                    extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                    value = extract_value[0]
                    if got_inputs.get('Mobile Number Link',None) is None:
                        got_inputs['Mobile Number Link'] = int(value)
                        pass
                
                elif need_input=='OTP Link':   # get data
                    value = nerTagger(inp_txt)
                    extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                    value = extract_value[0]
                    if got_inputs.get('OTP Link',None) is None:
                        got_inputs['OTP Link'] = int(value)
                        pass
                
                elif (need_input=='input_data') and (current.category == 'registration_to_open_account'):   # other inputs
                    if got_inputs.get('acc_type',None) is None:    ## didn't still get acc_type
                        got_inputs['acc_type'] = value
                        pass
                    elif got_inputs.get('new_name',None) is None:    ## didn't still get name
                        got_inputs['new_name'] = value.split(' ')
                        pass
                    elif got_inputs.get('new_email',None) is None:    ## didn't still get email
                        got_inputs['new_email'] = value
                        pass
                    elif got_inputs.get('new_PAN',None) is None:    ## didn't still get PAN
                        got_inputs['new_PAN'] = value
                        pass
                    elif got_inputs.get('new_Photo',None) is None:    ## didn't still get Photo
                        got_inputs['new_Photo'] = value
                        pass
                    elif got_inputs.get('new_Aadhaar',None) is None:    ## didn't still get Aadhaar
                        value = nerTagger(inp_txt)
                        extract_value = [value[i][0] for i in range(len(value)) if value[i][1]=='NUMBER'] 
                        value = extract_value[0]
                        got_inputs['new_Aadhaar'] = int(value)
                        pass
                    elif got_inputs.get('new_Address',None) is None:    ## didn't still get Address
                        got_inputs['new_Address'] = value
                        pass
                    elif got_inputs.get('new_Signature',None) is None:    ## didn't still get Signature
                        got_inputs['new_Signature'] = value
                        pass
                
                elif need_input=='Location':   # get data
                    if got_inputs.get('Location',None) is None:
                        got_inputs['Location'] = value
                        pass
                    
                # add_beneficiary-
                elif (need_input=='input_data') and (current.category == 'add_beneficiary'):   # other inputs
                    if got_inputs.get('receiver_IFSC',None) is None:    ## didn't still get receiver_IFSC
                        got_inputs['receiver_IFSC'] = str(value)
                        pass
                    elif got_inputs.get('receiver_bank_name',None) is None:    ## didn't still get receiver_bank_name
                        got_inputs['receiver_bank_name'] = str(value)
                        pass
                                            
                
                # reset_password-Net Banking 
                elif (need_input=='input_data') and (current.category == 'reset_password'):   # other inputs
                    if got_inputs.get('pass1',None) is None:    ## didn't still get password1
                        got_inputs['pass1'] = str(value)
                        pass
                    elif got_inputs.get('pass2',None) is None:    ## didn't still get password2
                        if got_inputs['pass1']!= str(value):
                            return 'पासवर्ड मेल नहीं खा रहा है। कृपया फिर से लिखिए!'
                        got_inputs['pass2'] = str(value)
                        pass
        ## ...
        
        prompt = get_expanded_txt()
        if prompt=='':
            cat=None
            need_input=None
            
            ## next expand category
            prompt = ''
            while True:
                current = full_fst_states_list[find_state_by_id(full_fst_states_list,
                                                                current.out_tr[0].next_state_id)
                                              ]
                if (current.state_type=='expand') and (not current.category.startswith('greeting')):
                    break
                elif current.prompt!='':
                    prompt = current.prompt
                    break
                elif current.category=='final':
                    break
            if prompt=='':
                return talk()
            else:
                next_s = full_fst_states_list[find_state_by_id(full_fst_states_list,
                                                               current.out_tr[0].next_state_id)
                                             ]
                if current.category == 'account_balance':
                    prompt = prompt.replace('2000',str(db.account_balance([got_inputs['Account Number'],
                                                                           got_inputs['Mobile Number'],
                                                                           got_inputs['OTP']
                                                                          ])))
                    
                elif ((current.category == 'payment') and (next_s.category == 'confirmation_by_customer') 
                                                      and (next_s.sub_category == 'Yes')):
                    prompt = prompt.replace('123456789',str(got_inputs['receiver_acc']))
                    prompt = prompt.replace('4567765688765abcd999',str(got_inputs['receiver_IFSC']))
                    prompt = prompt.replace('10500',str(got_inputs['receiver_amt']))
                
                elif ((current.category == 'payment') and (current.prompt.find('लेन - देन')!=-1) and 
                      (next_s.category == 'payment')):
                    res = db.payment([got_inputs['Account Number'],got_inputs['receiver_acc'],got_inputs['receiver_IFSC'],
                                got_inputs['receiver_amt'],got_inputs['Mobile Number'],got_inputs['OTP']])
                    if res:
                        prompt = prompt+"\n\nभुगतान सफल है|"
                    else:
                        prompt = prompt+"\n\nक्षमा करें, आपके खाते में पर्याप्त पैसा नहीं है|"

                elif current.category == 'forgot_password':
                    res = db.forgot_pass_net([got_inputs['Account Number'],got_inputs['Home Bank'],
                                              got_inputs['CIF Number'],got_inputs['OTP']])
                    if res:
                        prompt = prompt.replace('https://xxxbank . com/netbanking/password',
                                    'https://xxxbank.com/netbanking/password?acc_num='+str(got_inputs['Account Number']))
                    else:
                        prompt = "क्रेडेंशियल पुनर्प्राप्ति असफल हुवा| बाद में पुन: प्रयास करें|"
                        
                elif (current.category=='lost_debit_card') and (current.out_tr[0].label.find('dddd')!=-1):
                    need_input = 'input_data'
                    cat = -1
                    return prompt
                
                elif current.category == 'lost_debit_card':
                    res = db.block_card(['debit_card','blocked',got_inputs['Account Number'],got_inputs['Mobile Number'],
                                         got_inputs['debit_card_num'],got_inputs['OTP']])
                    if res:
                        prompt = prompt
                    else:
                        prompt = "आपका कार्ड blocking असफल हुवा| बाद में पुन: प्रयास करें|"
                    
                elif ((current.category == 'registration_to_open_account') and (next_s.category == 'goodbye')):
                    res = db.account_registration(["savings",got_inputs['new_name'][0],got_inputs['new_name'][1],
                                                   got_inputs['Mobile Number Link'],got_inputs['new_email'],
                                                   got_inputs['new_PAN'],got_inputs['new_Aadhaar'],
                                                   got_inputs['new_Address']])
                    if res:
                        desc = ("First name: "+got_inputs['new_name'][0]+", Last name: "+got_inputs['new_name'][1]+
                                "\nMobile Num: "+str(got_inputs['Mobile Number Link'])+"\nEmail: "+got_inputs['new_email']+
                                "\nPAN: "+got_inputs['new_PAN']+"\nAadhar: "+str(got_inputs['new_Aadhaar'])+"\nAddress: "+
                                got_inputs['new_Address'])
                        prompt = desc+"\n\n"+prompt
                    else:
                        prompt = "खाता पंजीकरण असफल। बाद में पुन: प्रयास करें|"
                        
                elif ((current.category == 'view_transactions')):
                    res = db.view_transactions([got_inputs['Account Number'],got_inputs['Mobile Number'],
                                                got_inputs['OTP']])
                    prompt = 'ये रहा आपके पिछले 10 लेन-देन के विवरण|\n\n'+res
                    
                elif ((current.category == 'branch_information')):
                    res = db.branch_info([got_inputs['Location']])
                    if res!='':
                        prompt = got_inputs['Location']+' के शाखाए है - \n'+res
                    else:
                        prompt = 'क्षमा कीजिये। '+got_inputs['Location']+' में कोई शाखाये नहीं है।'
                    
                # add_beneficiary-
                elif ((current.category == 'add_beneficiary') and (current.prompt.find('एक बार सारे')!=-1)):
                    prompt = prompt.replace('SBI564578',str(got_inputs['receiver_IFSC']))
                    prompt = prompt.replace('SBI',str(got_inputs['receiver_bank_name']))
                    prompt = prompt.replace('आगे बढ़े ?','\n-------\nपरिणाम')
                    
                    res = db.add_beneficiary([got_inputs['Account Number'], got_inputs['Mobile Number'], got_inputs['OTP'],
                                              got_inputs['receiver_IFSC'], got_inputs['receiver_bank_name']])
                    if res:
                        prompt = prompt + "\nलाभार्थी को सफलता पूर्वक जोड़ा गया|"
                    else:
                        prompt = prompt + "\nक्षमा करें, लाभार्थी जोड़ना असफल हुवा| बाद में पुन: प्रयास करें|"
                    
                
                # issue_check_book-
                elif ((current.category == 'issue_check_book')):
                    res = db.issue_cheque_book([got_inputs['Account Number'],got_inputs['Mobile Number'],
                                                got_inputs['OTP']])
                    if res==False:
                        prompt = "चेक बुक पहले ही जारी की जा चुकी है|"
                    else:                    
                        prompt = "नई चेक बुक, नंबर " + str(res) + " जारी कर दिया गया है"
                        

                
                # credit_card_details-Limit
                elif ((current.category == 'credit_card_details')):
                    res = db.credit_card_limit([got_inputs['Mobile Number'], got_inputs['OTP']])
                    prompt = prompt.replace('300000', str(res))

                
                # reset_password-Net Banking 
                elif ((current.category == 'reset_password') and (current.prompt.find('इस लिंक')!=-1)):
                    res = db.reset_pass_net([got_inputs['Account Number'], got_inputs['Home Bank'], 
                                             got_inputs['Mobile Number'], got_inputs['OTP'], got_inputs['pass1'], 
                                             got_inputs['pass2']])
                    if res:                    
                        prompt = prompt.replace('https://xxxbank . com/netbanking/password',
                                    'https://xxxbank.com/netbanking/password?acc_num='+str(got_inputs['Account Number']))
                    else:
                        prompt = "क्रेडेंशियल पुनर्प्राप्ति असफल हुवा| बाद में पुन: प्रयास करें|"
                
                
                        
                        
                if next_s.state_type=='normal':
                    need_input = 'input_data'
                    cat = -1
                elif next_s.state_type=='expand':
                    current = next_s
                    
                return prompt
        else:
            need_input = current.sub_category
            return prompt




# print(talk('reset_password-Net Banking'))
# print(talk('qwertyuiop'))




# db.auth_acc(int('128890'))
# db.auth_mob(int('128890'), int('9988776655'))
# db.auth_otp(int('128890'), int('9988776655'), int('9999'))
# db.account_balance([int('128890'), int('9988776655'), int('9999')])
# db.auth_cif(int('128890'), int('123456789123'))
# db.auth_branch(int('128890'), int('45233244'))
# db.forgot_pass_net([128890, 45233244, 123456789123, 9999])
# db.block_card(['debit_card', 'unblocked', 128890, 9988776655, 4561123475341596, 9999])
# db.view_transactions([128890, 9988776655, 9999])
# db.branch_info(['bengaluru'])
# db.reset_pass_net([128890, 45233244, 9988776655,  9999, 'qwertyuiop', 'qwertyuiop'])