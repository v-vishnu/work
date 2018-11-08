""""importing modules"""
import  json
from flask import Flask, redirect, url_for, abort, request
import DBconnection
import DBqueries


# Calling Flask API
APP = Flask(__name__)


CURSOR = DBconnection.init_db()


@APP.route('/login/<userID>,<password>', methods=['GET', 'POST'])
def login(userID, password):
    """"checking login details"""
    try:
        login_object = get_login_details(userID, password)
        if login_object:
            return redirect(url_for('accountdetails', userid=userID, password=password))
        return redirect(url_for('add_user'), code=307)
        # abort(500)
    except Exception as e:
        print(e)


def get_login_details(userid, pswrd):
    """"getting login details"""
    CURSOR.execute(DBqueries.login_query(), userid, pswrd)
    rows = CURSOR.fetchall()
    for row in rows:
        return row


@APP.route('/accountdetails/<userid>,<password>')
def accountdetails(userid, password):
    """" displaying account details"""""
    if verify_accnt_details(userid, password):
        accnt_detls_object = accnt_dtls(userid)
        return json.dumps({"accountnumber": accnt_detls_object[0],
                           "accounttype": accnt_detls_object[2],
                           "balance": accnt_detls_object[3],
                           "branch": accnt_detls_object[4]})
    # return "unauthorized error"
    abort(401)


def verify_accnt_details(userId, passwrd):
    """getting userID, password details from database"""
    CURSOR.execute(DBqueries.getaccnt_idpswrd_query(), userId, passwrd)
    rows = CURSOR.fetchall()
    for row in rows:
        return row


def accnt_dtls(userid):
    """getting account details from database"""
    CURSOR.execute(DBqueries.getacnt_dtls(), userid)
    rows = CURSOR.fetchall()
    for row in rows:
        return row


@APP.route('/transactiondetails/<accountnum>')
def transactiondetails(accountnum):
    """"  calculating transaction  details"""
    try:
        CURSOR.execute(DBqueries.transaction_query(), accountnum)
        rows = CURSOR.fetchall()
        if rows:
            for row in rows:
                transaction_details_list = list(map(str, list(row)))
                transaction_details_list.append(list(map(str, list(row))))
                CURSOR.execute(DBqueries.deposit_query(),
                               transaction_details_list[1],
                               transaction_details_list[0])
                CURSOR.commit()

                if transaction_details_list[2] <= transaction_details_list[3]:
                    CURSOR.execute(DBqueries.withdrawl_query(),
                                   transaction_details_list[2],
                                   transaction_details_list[0])
                    CURSOR.commit()
                    return redirect(url_for('finalbalancedetails',
                                            acntnum=accountnum))
        # return "there is no such account"
        abort(201)
    except Exception as e:
        print(e)


@APP.route('/finalbalancedetails/<acntnum>')
def finalbalancedetails(acntnum):
    """"route for displaying final balance details"""
    try:
        final_detls_object = get_final_balance(acntnum)
        if final_detls_object:
            return json.dumps({"accountnumber": final_detls_object[0],
                               "depositedamount": final_detls_object[1],
                               "withdrawnamount": final_detls_object[2],
                               "balance": final_detls_object[3]})

    except Exception as e:
        print(e)


def get_final_balance(accountnum):
    """ getting values of final balance details"""
    CURSOR.execute(DBqueries.finalbalnc_query(), accountnum)
    rows = CURSOR.fetchall()
    for row in rows:
        updated_details_list = list(map(str, list(row)))
        updated_details_list.append(list(map(str, list(row))))
        return updated_details_list


@APP.route('/add_user', methods=['POST'])
def add_user():
    """"adding user details"""
    try:
        userid = request.json['userID']
        acntnum = request.json['acntnum']
        if request.method == 'POST':
            CURSOR.execute(DBqueries.insert_usrIDdtls(), userid)
            CURSOR.commit()
            CURSOR.execute(DBqueries.insert_IDacntdtls(), acntnum, userid)
            CURSOR.commit()
            # return "User {} added successfully.".format(userid)
            abort(201)

    except Exception as e:
        print(e)


@APP.route('/add_accountdetails/<user>', methods=['POST'])
def add_accountdetails(user):
    """"adding accnt  details to new user"""
    _name = request.json['Name']
    _adrs = request.json['Address']
    _city = request.json['city']
    _email = request.json['email']
    _password = request.json['pwd']
    _acnttyp = request.json['acnttyp']
    _branch = request.json['branch']
    blnc = request.json['balance']
    if request.method == 'POST':
        CURSOR.execute(DBqueries.insert_all_userdtls(), _password,
                       _name, _email, _adrs, _city, user)
        CURSOR.commit()
        print(user)
        CURSOR.execute(DBqueries.insert_all_accntdtls(),
                       _acnttyp, blnc, _branch, user)
        CURSOR.commit()
        # return "User account details added successfully."
        abort(201)
    return "First create New User"


APP.run(debug=True)
