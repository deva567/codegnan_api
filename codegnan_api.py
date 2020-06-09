 
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
import configparser
import sys

#Intializing the config file through the commandline argument
config = configparser.ConfigParser()
config.read('config.ini')
mail_id=config.get('mail','UserName')
mail_Password=config.get('mail','Password')
admin_name=config.get('admin','admin')


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

        conn.execute('CREATE TABLE  IF NOT EXISTS users1(UserName TEXT PRIMARY KEY, Password TEXT, FullName TEXT, Email TEXT ,otp INT)')
        logging.info("Table created successfully.")
        msg="Database connected."
    except:
        logging.error("Database connectivity error occured.")
        msg="Database Connection issue ."

    finally:
        conn.close()
        logging.info("Connection closed")
    return msg 

def admin_access(UserName):
    """ This function can used by only ADMIN (vennam)
    """

    try:
        dict1={}
        print(UserName)
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


def otp_access(UserName):
    """This function can be used for validating OTP
       while changing Password
    """

    try:
        dict1={}
        print(UserName)
        conn = sql.connect('database.db')
        cur = conn.cursor()
        query=f"select * from users1 where UserName='{UserName}'"
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
            logging.info("fetched  %s details successfully. ",UserName)
    except:
        msg="Error while fetchind details"
        logging.info("Error while fetching  %s details. ",UserName)
    finally:
        conn.close()
    return return_list



def fetch_details(UserName):
    """ This function fetch all details of enduser based on UserName and \
        returns the details as list
    """
    try:
        dict1={}
        print(UserName)
        conn = sql.connect('database.db')
        cur = conn.cursor()
        query=f"select UserName,Password,FullName,Email from users1 where UserName='{UserName}'"
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
            logging.info("fetched  %s details successfully. ",UserName)
    except:
        msg="Error while fetchind details"
        logging.info("Error while fetching  %s details. ",UserName)
    finally:
        conn.close()
    return return_list


def del_user(UserName):

    """ This function will Delete userdetails 
        based on UserName
    """

    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        delete_query=f"Delete from users1 where UserName='{UserName}'"
        update = cur.execute(delete_query)
        conn.commit()
        logging.info("Deleted UserName from database based on UserName. ")
        msg="Deleted UserName from database based on UserName."
    except:
        logging,info("Deletion problem exists")
        msg="UserName deletion problem exists"
    finally:
        conn.close()
    return msg





def update_Password(UserName,Password):
    """ This function can be update Password of enduser based on UserName 
    after validating OTP 
    """

    try:
        conn = sql.connect('database.db')
        cur = conn.cursor()
        update_query=f"update users1 set Password='{Password}' where UserName='{UserName}'"
        update = cur.execute(update_query)
        conn.commit()
        logging.info("Password updated successfully in the database based on UserName. ")
        msg="Password updated successfully in the database based on UserName."
    except:
        logging.info("Password Updation problem exists")
        msg="Password Updation problem exists"
    finally:
        conn.close()
    return msg




@app.route('/')
def welcome():
    return "Welcome All"

@app.route('/UserNameAvailabity',methods=["GET"])
def UserName_availabity():


        
    """Let's Check the UserName available or not
    This is used for cheching avaliablity of UserName
    ---
    parameters:  
      - name: UserName
        in: query
        type: string
        required: true
    responses:
        200:
            description: This will be showing UserName avaliabilty as Output 
        
    """
    try:
    
        UserName=request.args.get("UserName")

        user_details=fetch_details(UserName)
        print(user_details[0]['UserName'])
        user_name=user_details[0]['UserName']
        if str(UserName)==str(user_name):
            logging.info(" %s already taken kindly choose another one .",UserName)
            msg="UserName is already taken kindly choose another one"
    except IndexError:
        logging.info(" %s is available .",UserName)
        msg="UserName is available."
    return msg
    

@app.route('/Signup',methods=["POST"])
def signup():
    
    """Sign Up Page
    This is using for signup
    ---
    parameters:  
      - name: UserName
        in: query
        type: string
        required: true
      - name: Password
        in: query
        type: string
        required: true
      - name: FullName
        in: query
        type: string
        required: true
      - name: Email
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns whether the user details successfully added or not
        
    """

    
    try:
        UserName=request.args.get("UserName")
        Password=request.args.get("Password")
        hashed_Password = hashlib.md5(Password.encode()).hexdigest() 
        FullName=request.args.get("FullName")
        Email=request.args.get("Email")
        with sql.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO users1 (UserName,Password,FullName,Email,otp) VALUES (?,?,?,?,NULL)",(UserName,hashed_Password,FullName,Email) )
            con.commit()
            msg = f"{UserName} details are stored successfully"
            logging.info(" %s details are stored in Database .",UserName)
    except:
        msg = f"kindly go and check UserName_availabity end_point for current {UserName}."
        logging.info(" kindly go and check UserName_availabity end_point for  %s.",UserName)

      
    finally:
        con.close()
        
    return msg

@app.route('/Login',methods=["GET"])
def login():
    """Let's Login Now 
    This is using for Login 
    ---
    parameters:  
      - name: UserName
        in: query
        type: string
        required: true
      - name: Password
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns the end user details
        
    """ 
    try:
        UserName=request.args.get("UserName")
        Password=request.args.get("Password")
        user_details=fetch_details(UserName)
        print(user_details[0]['Password'])
        hashed=user_details[0]['Password']
        UserName_key=user_details[0]['UserName']


        

        if UserName==UserName_key and hashed==hashlib.md5(Password.encode()).hexdigest():
            user_details=fetch_details(UserName)
            dict1 = {'result':user_details}
            print(dict1)
        else:
            dict1={"Error":"Invalid  UserName or Password , kindly check ."}
    except IndexError:
        dict1={"Error":"Invalid  UserName and UserName not available in Database."}

    return Response(json.dumps(dict1),  mimetype='application/json')





    
@app.route('/Admin',methods=["GET"])
def extract():
    """Admin Page
    This can be used by only ADMIN
    ---
    parameters:  
      - name: UserName
        in: query
        type: string
        required: true
      - name: Password
        in: query
        type: string
        required: true
    responses:
        200:
            description: The output returns as all user details
        
    """ 
    try:

        UserName=request.args.get("UserName")
        Password=request.args.get("Password")
        user_details=fetch_details(UserName)
        print(user_details[0]['Password'])
        hashed=user_details[0]['Password']
        UserName_key=user_details[0]['UserName']

        if UserName==admin_name:
            if UserName==UserName_key and hashed==hashlib.md5(Password.encode()).hexdigest():
                user_details=admin_access(UserName)
                dict1 = {'result':user_details}
                print(dict1)
            else:
                dict1={"Error":"Invalid admin UserName or admin Password , kindly check ."}
        else:
            dict1={"Error":"You are not admin for this API ."}
    except IndexError:
        dict1={"Error":"Kindly enter correct  admin UserName or admin Password ."}

        
    return Response(json.dumps(dict1),  mimetype='application/json')
    


@app.route('/ChangePassword',methods=["POST"])
def change_Password():
    """Let's Change Password 
    This is using for Changing Password based on UserName and validation of OTP
    ---
    parameters: 
      - name: UserName
        in: query
        type: string
        required: true
      - name: OTP
        in: query
        type: number
        required: true
      - name: NewPassword
        in: query
        type: string
        required: true
      - name: API_KEY
        in: header
        description: an authorization header
        required: true
        type: string
    responses:
        200:
            description: The output returns whether the Password changed sucessfully or not
        
    """ 
    try:

        UserName=request.args.get("UserName")
        validate_otp=request.args.get("OTP")    
        NewPassword=request.args.get("NewPassword")
        hashed_Password = hashlib.md5(NewPassword.encode()).hexdigest() 
        with open('api.key', 'r') as apikey:
            key=apikey.read().replace('\n', '')
        if request.headers.get('API_KEY') == key:
           if str(username)==str(validate_otp):
                    msg=update_password(username,hashed_password)
                    #This function calling makes the user use OTP until Password gets changed after that validity of OTP will be expired.
                    new_otp=randint(10000,100000)
                    # This will checks the new generated OTP and old OTP
                    if str(otp)==str(new_otp):
                        new_otp=randint(10000,100000)
                        update_otp(UserName,new_otp)
                    else:
                        update_otp(UserName,new_otp)
            else:
                msg="Something went wrong check the OTP or UserName!!!!"
                logging.info("Something went wrong check the OTP or UserName!!!!")
        else:
            msg="Enter correct API KEY for Authentication."
    except IndexError:
        msg=f"{UserName} does not exist , kindly enter correct UserName."
    return msg

@app.route('/DeleteUserName',methods=["POST"])
def delete_UserName():
    """Let's Change Password 
    This is using for Changing Password based on UserName and validation of OTP
    ---
    parameters: 
      - name: UserName
        in: query
        type: string
        required: true
      - name: Password
        in: query
        type: string
        required: true
      - name: API_KEY
        in: header
        description: an authorization header
        required: true
        type: string
    responses:
        200:
            description: The output returns whether the Password changed sucessfully or not
        
    """ 

    try:

        UserName=request.args.get("UserName")
        Password=request.args.get("Password")
        user_details=fetch_details(UserName)
        hashed=user_details[0]['Password']
        UserName_key=user_details[0]['UserName']

        with open('api.key', 'r') as apikey:
            key=apikey.read().replace('\n', '')
        if request.headers.get('API_KEY') == key:
            if UserName==UserName_key and hashed==hashlib.md5(Password.encode()).hexdigest():
               msg=del_user(UserName)
               dict1={"Message":msg}
                
            else:
                dict1={"Message":"Invalid  UserName or Password , kindly check ."}
        else:
            dict1={"Message":"Enter API KEY for Authentication ."}
    except IndexError:
        dict1={"Message":"UserName not available ."}
    return Response(json.dumps(dict1),  mimetype='application/json')


if __name__=='__main__':
    logging.info("Started program.")

    create_database() #Intializing Database 
    logging.info("Database Intialized successfully")
    app.run(debug=True) #Running our FLASK APP
    
    
