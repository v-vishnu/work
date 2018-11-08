from flask import Flask, redirect, url_for, jsonify
import pyodbc


def login_query():
    query = """SELECT userID, Password from bankuser_details
            where userID = ? and Password = ?"""
    return query


def getaccnt_idpswrd_query():
    query = """SELECT a.userID,
            b.password from bankaccount_details
             a join bankuser_details b
            on a.userID=b.userID 
            where b.userID=? and b.password=? """
    return query


def getacnt_dtls():
    query = "SELECT * from bankaccount_details where userID=?"
    return query


def transaction_query():
    query = """select t.accountnumber,
                   convert(decimal,depositedamount)depositedamount, 
                   convert(decimal,t.withdrawnamount)withdrawnamount, 
                   b.balance from transaction_details t join
                    bankaccount_details b on
                    t.accountnumber=b.accountnumber
                    where t.accountnumber=?"""
    return query


def deposit_query():
    query = "UPDATE bankaccount_details  SET balance = balance +? where accountnumber=?"
    return query


def withdrawl_query():
    query = "UPDATE bankaccount_details SET balance = balance -? where accountnumber=?"
    return query


def finalbalnc_query():
    query = """select t.accountnumber, convert(decimal, depositedamount)depositedamount, 
         convert(decimal,t.withdrawnamount)withdrawnamount
                   , b.balance from transaction_details t join
                    bankaccount_details b on t.accountnumber=b.accountnumber
                    wehre t.accountnumber=?"""
    return query


def insert_usrIDdtls():
    sql = "INSERT INTO bankuser_details(userID) VALUES(?)"
    return sql


def insert_IDacntdtls():
    sql_accnt = "INSERT INTO bankaccount_details(accountnumber,userID) VALUES(?,?)"
    return sql_accnt


def insert_all_userdtls():
    sql = """UPDATE bankuser_details SET password=?, Name=?,
           Email=?, Addressline=?, City=?   WHERE userID=?"""
    return sql


def insert_all_accntdtls():
    sql = """"UPDATE bankaccount_details SET  accounttype=?," 
          " balance=?, branch=? WHERE userID=? """
    return sql





