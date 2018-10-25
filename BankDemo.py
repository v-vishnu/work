""""importing modules"""
from flask import Flask, redirect, url_for, jsonify
import pyodbc


app = Flask(__name__)


def init_db():
    """"connecting to database"""
    server = '192.168.18.36'
    db = 'HBK_Test'
    user = 'kailashp'
    password = 'Welcome@731'
    con = pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                         'SERVER=' + server + ';DATABASE=' + db +
                         ';UID=' + user + ';PWD=' + password)
    cursor = con.cursor()
    return cursor


cursor = init_db()


@app.route('/login/<userID>,<password>')
def login(userID, password):
    """"checking login details"""
    login_object = get_login_details(userID, password)
    if type(login_object) is pyodbc.Row:
        return redirect(url_for('accountdetails', userid=userID))
    return "UserID or password is invalid"


def get_login_details(userID, pswrd):
    """"getting login details"""
    cursor.execute("SELECT userID, "
                   " Password from bankuser_details"
                   " where userID = ? and Password = ?",
                   userID, pswrd)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            return row


@app.route('/accountdetails/<userid>')
def accountdetails(userid):
    """" displaying account details"""
    accnt_detls_object = get_accnt_details(userid)
    if type(accnt_detls_object) is pyodbc.Row:
        return jsonify({"accountnumber": accnt_detls_object[0],
                        "accounttype": accnt_detls_object[2],
                        "balance": accnt_detls_object[3],
                        "branch": accnt_detls_object[4]})
    return "UserID or password is invalid"


def get_accnt_details(userid):
    """getting userID details from database"""
    cursor.execute("SELECT * from bankaccount_details"
                   " where userID = ?", userid)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            return row


@app.route('/transactiondetails/<accountnum>')
def transactiondetails(accountnum):
    """"  calculating transaction  details"""
    cursor.execute("select t.accountnumber, "
                   "convert(decimal,depositedamount)depositedamount,"
                   "convert(decimal,t.withdrawnamount)withdrawnamount,"
                   "b.balance from transaction_details t join"
                   " bankaccount_details b on"
                   " t.accountnumber=b.accountnumber"
                   " where t.accountnumber=?", accountnum)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            transaction_details_list = list(map(str, list(row)))
            transaction_details_list.append(list(map(str, list(row))))
            cursor.execute("UPDATE bankaccount_details"
                           " SET balance = balance +?"
                           " where accountnumber=?",
                           transaction_details_list[1],
                           transaction_details_list[0])
            cursor.commit()

            if transaction_details_list[2] <= transaction_details_list[3]:
                cursor.execute("UPDATE bankaccount_details"
                               " SET balance = balance -?"
                               " where accountnumber=?",
                               transaction_details_list[2],
                               transaction_details_list[0])
                cursor.commit()
                return redirect(url_for('finalbalancedetails',
                                        acntnum=accountnum))
    return "UserID or password is invalid"


@app.route('/finalbalancedetails/<acntnum>')
def finalbalancedetails(acntnum):
    """"route for displaying final balance details"""
    final_detls_object = get_final_balance(acntnum)
    if final_detls_object:
        return jsonify({"accountnumber": final_detls_object[0],
                        "depositedamount": final_detls_object[1],
                        "withdrawnamount": final_detls_object[2],
                        "balance": final_detls_object[3]})


def get_final_balance(accountnum):
    """ getting values of final balance details"""
    cursor.execute("select t.accountnumber,"
                   "convert(decimal, depositedamount)depositedamount,"
                   "convert(decimal,t.withdrawnamount)withdrawnamount"
                   ", b.balance from transaction_details t join"
                   " bankaccount_details b on t.accountnumber=b.accountnumber"
                   " where t.accountnumber=?", accountnum)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            updated_details_list = list(map(str, list(row)))
            updated_details_list.append(list(map(str, list(row))))
            return updated_details_list


app.run(debug=True)
