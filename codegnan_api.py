

from flask import Flask, request
import pandas as pd
import flasgger
from flasgger import Swagger
from flask_ngrok import run_with_ngrok
import sqlite3 as sql
from flask import jsonify
from flask import Response
import json
import hashlib
import smtplib 
from random import randint
import logging
import configparser
import sys

#Intializing the config file through the commandline argument
config = configparser.ConfigParser()
config.read('config.ini')
mail_id=config.get('mail','username')
mail_password=config.get('mail','password')
admin_name=config.get('admin','admin')

#creating the Flask_API log file for flow of the API
logging.basicConfig( filename='flask_api_log.log', filemode='w',format='%(asctime)s - %(message)s', level=logging.INFO)
logging.info('Flask_API imported necessary libraries into program.')

#Intializing FLASK App
app=Flask(__name__)
#Intializing flasgger which helps to creating the better interaction between enduser and Flask API 
Swagger(app)
#run_with_ngrok(app)

def create_database():
    """This function will be used for intializing Database and
       create the table 
    """
    try:
        conn = sql.connect('database.db')
        logging.info("Opened database successfully.")

        conn.execute('CREATE TABLE  IF NOT EXISTS users1(username TEXT PRIMARY KEY, password TEXT, fullname TEXT, email TEXT ,mobilenumber TEXT,otp INT)')
        logging.info("Table created successfully.")
        msg="Database connected."
    except:
        logging.error("Database connectivity error occured.")
        msg="Database Connection issue ."

    finally:
        conn.close()
        logging.info("Connection closed")
    return msg 

def admin_access(username):
    """ This function can used by only ADMIN (vennam)
    """

    try:
        dict1={}
        print(username)
        conn = sql.connect('database.db')
        cur = conn.cursor()
        query="select * from users1"
        result = cur.execute(query)
        column_names = []
        return_list = []
        for row in result.description:
            column_names.append(row[0])
        result = result.fetchall()
        print(result)
        for res in range(len(result)):
            temp_dict = {}
            for col in range(len(column_names)):
                temp_dict.update({column_names[col]:result[res][col]})
            return_list.append(temp_dict)
            msg="fetched details successfully."
            logging.info("fetched  all  details successfully. ")
    except:
        msg="Error while fetchind details"
        logging.info("Error while fetching all details. ")
    finally:
        conn.close()
    return return_list


def otp_access(username):
    """This function can be used for validating OTP
       while changing password
    """

    try:
        dict1={}
        print(username)
        conn = sql.connect('database.db')
        cur = conn.cursor()
        query=f"select * from users1 where username='{username}'"
        result = cur.execute(query)
        column_names = []
        return_list = []
        for row in result.description:
            column_names.append(row[0])
        result = result.fetchall()
        print(result)
        for res in range(len(result)):
            temp_dict = {}
            for col in range(len(column_names)):
                temp_dict.update({column_names[col]:result[res][col]})
            return_list.append(temp_dict)
            msg="fetched details successfully."
            logging.info("fetched  %s details successfully. ",username)
    except:
        msg="Error while fetchind details"
        logging.info("Error while fetching  %s details. ",username)
    finally:
        conn.close()
    return return_list



def fetch_details(username):
    """ This function fetch all details of enduser based on username and \
        returns the details as list
    """
    try:
        dict1={}
        print(username)
        conn = sql.connect('database.db')
        cur = conn.cursor()
        query=f"select username,password,fullname,email,mobilenumber from users1 where username='{username}'"
        result = cur.execute(query)
        column_names = []
        return_list = []
        for row in result.description:
            column_names.append(row[0])
        result = result.fetchall()
        print(result)
        for res in range(len(result)):
            temp_dict = {}
            for col in range(len(column_names)):
                temp_dict.update({column_names[col]:result[res][col]})
            return_list.append(temp_dict)
            msg="fetched details successfully."
            logging.info("fetched  %s details successfully. ",username)
    except:
        msg="Error while fetchind details"
        logging.info("Error while fetching  %s details. ",username)
    finally:
        conn.close()
    return return_list


def update_otp(username,otp):

    """ This function will update OTP before sending mail to enduser 
        for validation purpose
    """

    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        update_query=f"update users1 set otp={otp} where username='{username}'"
        update = cur.execute(update_query)
        conn.commit()
        logging.info("OTP updated in the database based on username. ")
        msg="OTP updated in the database based on username."
    except:
        logging,info("OTP Updation problem exists")
        msg="OTP Updation problem exists"
    finally:
        conn.close()
    return msg

def update_password(username,password):
    """ This function can be update password of enduser based on username 
    after validating OTP 
    """

    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        update_query=f"update users1 set password='{password}' where username='{username}'"
        update = cur.execute(update_query)
        conn.commit()
        logging.info("password updated successfully in the database based on username. ")
        msg="password updated successfully in the database based on username."
    except:
        logging.info("password Updation problem exists")
        msg="password Updation problem exists"
    finally:
        conn.close()
    return msg


def send_mail(email_id,OTP):
    """ This function will be sending the OTP mails to enduser's registered mail id  
    NOTE: The Mail id should be valid 
    """
    logging.info("The mail has been set to user with OTP")
 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    s.ehlo()
    # start TLS for security 
    s.starttls() 

    # Authentication 
    s.login(mail_id,mail_password) 
    logging.info("The user Authentication is verified.")
    message = str(OTP)

    # sending the mail 
    s.sendmail(mail_id, email_id, message) 

    # terminating the session 
    s.quit() 
    logging.info("The mail has been sent to user with OTP.")


@app.route('/')
def welcome():
    return "Welcome All"

@app.route('/username_availabity',methods=["GET"])
def username_availabity():


        
    """Let's Check the Username available or not
    This is used for cheching avaliablity of Username
    ---
    parameters:  
      - name: username
        in: query
        type: string
        required: true
    responses:
        200:
            description: This will be showing Username avaliabilty as Output 
        
    """
    try:
    
        username=request.args.get("username")

        user_details=fetch_details(username)
        print(user_details[0]['username'])
        user_name=user_details[0]['username']
        if str(username)==str(user_name):
            logging.info(" %s already taken kindly choose another one .",username)
            msg="Username is already taken kindly choose another one"
    except IndexError:
        logging.info(" %s is available .",username)
        msg="Username is available."
    return msg
    

@app.route('/signup',methods=["POST"])
def signup():
    
    """Sign Up Page
    This is using for signup
    ---
    parameters:  
      - name: username
        in: query
        type: string
        required: true
      - name: password
        in: query
        type: string
        required: true
      - name: fullname
        in: query
        type: string
        required: true
      - name: email
        in: query
        type: string
        required: true
      - name: mobile number
        in: path
        type: number
        required: true
    responses:
        200:
            description: The output returns whether the user details successfully added or not
        
    """

    
    try:
        username=request.args.get("username")
        password=request.args.get("password")
        hashed_password = hashlib.md5(password.encode()).hexdigest() 
        fullname=request.args.get("fullname")
        email=request.args.get("email")
        mobilenumber=request.args.get("mobilenumber")
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users1 (username,password,fullname,email,mobilenumber,otp) VALUES (?,?,?,?,?,?)",(username,hashed_password,fullname,email,mobilenumber,0) )
            con.commit()
            msg = f"{username} details are stored nsuccessfully"
            logging.info(" %s details are stored in Database .",username)
    except:
        msg = "kindly go and check username_availabity end_point for current Username."
        logging.info(" kindly go and check username_availabity end_point for  %s.",username)

      
    finally:
        con.close()
        
    return msg

@app.route('/login',methods=["GET"])
def login():
    """Let's Login Now 
    This is using for Login 
    ---
    parameters:  
      - name: username
        in: query
        type: string
        required: true
      - name: password
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns the end user details
        
    """ 
    try:
        username=request.args.get("username")
        password=request.args.get("password")
        user_details=fetch_details(username)
        print(user_details[0]['password'])
        hashed=user_details[0]['password']
        username_key=user_details[0]['username']


        

        if username==username_key and hashed==hashlib.md5(password.encode()).hexdigest():
            user_details=fetch_details(username)
            dict1 = {'result':user_details}
            print(dict1)
        else:
            dict1={"Error":"Invalid  username or password , kindly check ."}
    except IndexError:
        dict1={"Error":"Invalid  username and username not available in Database."}

    return Response(json.dumps(dict1),  mimetype='application/json')





    
@app.route('/admin',methods=["GET"])
def extract():
    """Admin Page
    This can be used by only ADMIN
    ---
    parameters:  
      - name: username
        in: query
        type: string
        required: true
      - name: password
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns as all user details
        
    """ 
    try:

        username=request.args.get("username")
        password=request.args.get("password")
        user_details=fetch_details(username)
        print(user_details[0]['password'])
        hashed=user_details[0]['password']
        username_key=user_details[0]['username']

        if username==admin_name:


            if username==username_key and hashed==hashlib.md5(password.encode()).hexdigest():
                user_details=admin_access(username)
                dict1 = {'result':user_details}
                print(dict1)
            else:
                dict1={"Error":"Invalid admin username or admin password , kindly check ."}
        else:
            dict1={"Error":"You are not admin for this API ."}
    except IndexError:
        dict1={"Error":"Kindly enter correct  admin username or admin password ."}

        
    return Response(json.dumps(dict1),  mimetype='application/json')
    
    
@app.route('/forgot_password',methods=["POST"])
def forgot_password():
    """ Forgot Password
    This is using for forgot password.
    ---
    parameters: 
      - name: username
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns message whether mail has been sent or not
    
    """ 
    OTP=randint(10000,100000)
    print(OTP)
    logging.info("OTP generated successfully. ")
    username=request.args.get("username")
    try:

        user_details=fetch_details(username)
        email_id=user_details[0]['email']



        update_otp(username,OTP)
        send_mail(email_id,OTP)
        logging.info("sendmail function called. ")
        msg="Mail has been sent to Registered mail id."
    except IndexError:
        logging.info("%s username details not found kindly enter valid Username. ",username)
        msg=f"{username} details not found kindly enter valid Username."

    return msg

@app.route('/change_password',methods=["POST"])
def change_password():
    """Let's Change Password 
    This is using for Changing Password based on Username and validation of OTP
    ---
    parameters: 
      - name: username
        in: query
        type: string
        required: true
      - name: OTP
        in: query
        type: number
        required: true
      - name: new_password
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns whether the Password changed sucessfully or not
        
    """ 
    username=request.args.get("username")
    validate_otp=request.args.get("OTP")    
    new_password=request.args.get("new_password")
    hashed_password = hashlib.md5(new_password.encode()).hexdigest() 

    user_details=otp_access(username)
    print("the otp in  db")

    print(user_details[0]['otp'])
    otp=user_details[0]['otp']
    if str(otp)==str(validate_otp):
            msg=update_password(username,hashed_password)
            #This function calling makes the user use OTP until password gets changed after that validity of OTP will be expired.
            new_otp=randint(10000,100000)
            # This will checks the new generated OTP and old OTP
            if str(otp)==str(new_otp):
                new_otp=randint(10000,100000)
                update_otp(username,new_otp)
            else:
                update_otp(username,new_otp)

    else:
        msg="Something went wrong check the OTP or Username!!!!"
        logging.info("Something went wrong check the OTP or Username!!!!")

    return msg


if __name__=='__main__':
    logging.info("Started program.")

    create_database() #Intializing Database 
    logging.info("Database Intialized successfully")
    app.run(debug=True) #Running our FLASK APP
    
    