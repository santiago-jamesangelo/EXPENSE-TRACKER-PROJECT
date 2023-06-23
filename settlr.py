import mariadb
import sys
import pwinput
from tabulate import tabulate
from textwrap import dedent

emails = ["@gmail.com", "@up.edu.ph", "@yahoo.com", "@hotmail.com"]

def show_expenses(attributes, cur, current_user):
    cur.execute("SELECT "+attributes+" FROM expense WHERE expense_id IN (SELECT expense_id FROM expense_details WHERE username = ?);",(current_user,))
    
    if(cur.rowcount == 0):
        print("You are not part of any expenses yet!")
        return False
    else:
        result = cur.fetchall()
        col_name = [description[0] for description in cur.description]
        print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

def show_users_not_friend(cur, current_user):
    cur.execute("SELECT username FROM user WHERE NOT username=ANY(SELECT friend_username FROM user_friend WHERE username=?) AND NOT username=?;",(current_user, current_user,))
    if(cur.rowcount == 0):
        print("There are no other users to add as friends yet!")
        return False
    else:
        result = cur.fetchall()
        col_name = [description[0] for description in cur.description]
        print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

        not_friends_list = [i[0] for i in result]
        
        return not_friends_list

def show_users_friend(cur, current_user):
    cur.execute("SELECT username FROM user WHERE username=ANY(SELECT friend_username FROM user_friend WHERE username=?) AND NOT username=?;",(current_user, current_user,))
    if(cur.rowcount == 0):
        print("You have no friends yet!")
        return False
    else:
        result = cur.fetchall()
        col_name = [description[0] for description in cur.description]
        print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))
        
        friends_list = [i[0] for i in result]

        return friends_list

def show_friend_details(cur, friend):
    cur.execute("SELECT username, email, name FROM user WHERE username=?;",(friend,))
    result = cur.fetchall()
    col_name = [description[0] for description in cur.description]
    print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

def users_list(cur):
    cur.execute("SELECT username FROM user;")
    rows = cur.fetchall()
    user_list = [i[0] for i in rows]
    return user_list

def show_groups(cur,current_user):
    cur.execute("SELECT * FROM friend_group WHERE group_id IN (SELECT group_id FROM group_details WHERE username=?);",(current_user,))
    
    if(cur.rowcount == 0):
        print("You are not part of any groups yet!")
        return False
    else:
        result = cur.fetchall()
        col_name = [description[0] for description in cur.description]
        print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

def login(cur):
    username = input("\nUsername: ")
    password = pwinput.pwinput(prompt='Password: ')
    
    cur.execute("SELECT username FROM user")

    user_list = [i[0] for i in cur.fetchall()]
    
    if(username in user_list):
        cur.execute("SELECT password FROM user WHERE username = ?",(username,))
        
        pw = cur.fetchone()[0]

        # print(pw)
        
        if(password == pw):
            return username
        else:
            print("Wrong password!")  
    else:
        print("Username not found!")

def signUp(cur, mydb):
    cur.execute("SELECT username FROM user")
    user_list = [i[0] for i in cur.fetchall()] #for checking if the username already exists to avoid integrity error where primary key tries to be duplicated
    
    username = input("Username: ")
    
    if(username in user_list):
        print("Username already exists!")
        return None

    if(len(username) > 20):
        print("Username is too long!")
        return None

    correctEmail = False
    email = input("Email: ")

    if(len(email) > 30):
        print("Email is too long!")
        return None

    for i in emails:
        if(i in email):
            correctEmail = True

    if(correctEmail == False):
        print("Invalid email!")
        return None

    name = input("Name: ")

    if(len(name) > 30):
        print("Name is too long!")
        return None

    password = pwinput.pwinput(prompt='Password: ')

    if(len(password) > 10):
        print("Password is too long!")
        return None
    
    cur.execute("INSERT INTO user VALUES(?,?,?,?)",(username,email,name,password,))
    mydb.commit()

    return username

def edit_profile(cur, mydb, current_user):
    cur.execute("SELECT name, username, email FROM user WHERE username=?;",(current_user,))
    u = cur.fetchone()
    print(dedent("""
    -------------------------------
    |           PROFILE           |
    -------------------------------
    """))
    print("\nName: ", u[0])
    print("Username: ", u[1])
    print("Email: ", u[2])
    print("_______________________________")
    while True:
        print(dedent("""
        ==================
          UPDATE PROFILE
        ================== 
        [1] Email
        [2] Name
        [3] Password
        [4] Back
        __________________
        """))
        try:
            attribute = int(input("Enter choice [1-4]: "))
        except ValueError:
            print("Invalid input!")
            continue

        if(attribute == 1):
            correctEmail  = False
            value = input("New value: ")

            if(len(value) > 30):
                print("Email is too long!")
                return None

            for i in emails:
                if(i in value):
                    correctEmail = True

            if(correctEmail == False):
                print("Invalid email!")
                return None

            cur.execute("UPDATE user SET email = ? WHERE username = ?;",(value,current_user,))
            mydb.commit()
        elif(attribute == 2):
            value = input("New value: ")
            
            if(len(value) > 30):
                print("Name is too long!")
                return None

            cur.execute("UPDATE user SET name = ? WHERE username = ?;",(value,current_user,))
            mydb.commit()
        elif(attribute == 3):
            value = input("New value: ")

            if(len(value) > 10):
                print("Password is too long!")
                return None

            cur.execute("UPDATE user SET password = ? WHERE username = ?;",(value,current_user,))
            mydb.commit()
        elif(attribute == 4):
            break
        else:
            print("Invalid input!")

def add_group_expense(cur, mydb, current_user):
    result = show_groups(cur,current_user)
    if(result is not False):
        groupname = input("\nWhat's the name of the group that you will share the expense with? ")

        cur.execute("SELECT group_id FROM friend_group WHERE group_name=?;",(groupname,))
        group_id = cur.fetchone()

        if(group_id == None):
            print("Group not found!")
            return None
        else:
            group_id = group_id[0]

        cur.execute("SELECT username FROM group_details WHERE group_id=? AND username=?;",(group_id,current_user,))
        username = cur.fetchone()
        
        if(username == None):
            print("You are not a part of this group!")
            return None
        
        try:
            total = round(float(input("Total amount of the expense: ")),2)
        except ValueError:
            print("Total invalid!")
            return None

        if(total > 9999.99):
            print("Total invalid!")
            return None

        description = input("Description of the expense: ")

        if(len(description) > 30):
            print("Description is too long!")
            return None

        indiv_paid = input("Username of who paid for the expense: ")

        cur.execute("SELECT username FROM group_details WHERE group_id=? AND username=?;",(group_id,indiv_paid,))
        username = cur.fetchone()
        
        if(username == None):
            print("This user is not a part of this group!")
            return None
        
        cur.execute("SELECT COUNT(username) FROM group_details WHERE group_id=? GROUP BY group_id",(group_id,))
        member_count = int(cur.fetchone()[0])
        cur.execute("SELECT * FROM expense;")
        result = cur.fetchall()
        expense_id = len(result)
        cur.execute("ALTER TABLE expense AUTO_INCREMENT=?;",(expense_id,))
        cur.execute("INSERT INTO expense (balance,total_amount,description_expense,individual_paid,group_id) VALUES (?,?,?,?,?);", (total-(total/member_count), total, description, indiv_paid, group_id,))
        mydb.commit()

        cur.execute("SELECT username FROM group_details WHERE group_id=?",(group_id,))
        user_list = cur.fetchall()

        for i in user_list:
            for j in i:
                if(j == indiv_paid):
                    cur.execute("INSERT INTO expense_details (username,expense_id,paid,amount) VALUES (?,?,?,?);", (j, expense_id+1, "Paid", 0,))
                    mydb.commit()
                else:
                    cur.execute("INSERT INTO expense_details (username,expense_id,paid,amount) VALUES (?,?,?,?);", (j, expense_id+1, "Not paid", total/member_count,))
                    mydb.commit()

        print("\nExpense successfully added!")

def add_indiv_expense(cur, mydb, current_user):
    result = show_users_friend(cur, current_user)
    if(result is not False):
        friend_username = input("\nWho did you share the expense with?: ")

        
        cur.execute("SELECT username FROM user_friend WHERE username=? AND friend_username=?",(current_user,friend_username))

        if(cur.fetchone() == None):
            print("You are not friends with this user!")
            return None
        
        try:
            total = round(float(input("Total amount of the expense: ")),2)
        except ValueError:
            print("Total invalid!")
            return None

        if(total > 9999.99):
            print("Total invalid!")
            return None

        description = input("Description of the expense: ")

        if(len(description) > 30):
            print("Description is too long!")
            return None

        indiv_paid = current_user

        cur.execute("SELECT * FROM expense;")
        result = cur.fetchall()
        expense_id = len(result)
        cur.execute("ALTER TABLE expense AUTO_INCREMENT=?;",(expense_id,))
        cur.execute("INSERT INTO expense (balance,total_amount,description_expense,individual_paid,username) VALUES (?,?,?,?,?);", (total/2, total, description, indiv_paid, friend_username))
        mydb.commit()

        cur.execute("INSERT INTO expense_details (username,expense_id,paid,amount) VALUES (?,?,?,?);", (current_user, expense_id+1, "Paid", 0,))
        cur.execute("INSERT INTO expense_details (username,expense_id,paid,amount) VALUES (?,?,?,?);", (friend_username, expense_id+1, "Not paid", total/2,))
        mydb.commit()

        print("\nExpense successfully added!")

def delete_expense(cur, mydb, current_user):
    result = show_expenses("expense_id,description_expense", cur, current_user)
    if(result is not False):
        delete = int(input("\nExpense id of the expense that you want to delete: "))
        
        cur.execute("SELECT expense_id FROM expense WHERE expense_id IN (SELECT expense_id FROM expense_details WHERE username = ?);",(current_user,))
        rows = cur.fetchall()
        id_list = [i[0] for i in rows]
        
        if(delete in id_list):
            cur.execute("DELETE FROM expense WHERE expense_id=?;",(delete,))
            cur.execute("DELETE FROM expense_details WHERE expense_id=?;",(delete,))
            mydb.commit()
            print("\nExpense successfully deleted!")
        else:
            print("Expense ID ",delete," does not exist.")

def search_expense(cur, current_user):
    result = show_expenses("expense_id,description_expense", cur, current_user)
    if(result is not False):
        search = int(input("\nExpense id of the expense that you want details of: "))
        
        cur.execute("SELECT expense_id FROM expense WHERE expense_id IN (SELECT expense_id FROM expense_details WHERE username = ?);",(current_user,))
        rows = cur.fetchall()
        id_list = [i[0] for i in rows]
        
        if(search in id_list):
            cur.execute("SELECT * FROM expense WHERE expense_id=?;",(search,))
            result = cur.fetchall()
            col_name = [description[0] for description in cur.description]
            print("\nHere are the details of the expense:")
            print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))
        else:
            print("Expense ID ",search," does not exist.")

def edit_expense(cur, mydb, current_user):
    result = show_expenses("expense_id,status,balance,total_amount,description_expense", cur, current_user)
    if(result is not False):
        update = int(input("\nExpense id of the expense that you want to update: "))
        
        cur.execute("SELECT expense_id FROM expense WHERE expense_id IN (SELECT expense_id FROM expense_details WHERE username = ?);",(current_user,))
        rows = cur.fetchall()
        id_list = [i[0] for i in rows]
        
        if(update in id_list):
            while True:
                print(dedent("""
                ==================
                  UPDATE EXPENSE
                ==================
                [1] Status
                [2] Balance
                [3] Description
                [4] Back
                _________________
                """))
                try:
                    attribute = int(input("Enter choice [1-4]: "))
                except ValueError:
                    print("Invalid input!")
                    continue

                if(attribute == 1):
                    value = input("New value: ")

                    if(value != "Paid" and value != "Not paid"):
                        print("Value should only be Paid or Not paid")
                        return None

                    cur.execute("UPDATE expense SET status = ? WHERE expense_id = ?;",(value,update,))
                    cur.execute("SELECT status FROM expense WHERE expense_id = ?;",(update,))
                    status = cur.fetchone()[0]
                    
                    if(status == 'Paid'):
                        cur.execute("UPDATE expense_details SET amount = ?, paid = 'Paid' WHERE expense_id = ?;",(0,update,))
                        cur.execute("UPDATE expense SET balance = ? WHERE expense_id = ?",(0,update,))
                        print("Status successfully updated!")
                    mydb.commit()
                elif(attribute == 2):
                    try:
                        cur.execute("SELECT group_id FROM expense where expense_id = ?",(update,))
                        result = cur.fetchone()[0]
                        if(result is None):
                            cur.execute("SELECT username FROM expense WHERE expense_id = ?;",(update,))
                            payer = cur.fetchone()[0]
                            cur.execute("SELECT balance FROM expense WHERE expense_id = ?;",(update,))
                            balance = float(cur.fetchone()[0])
                            if(balance == 0):
                                print(payer,"has already paid!")
                                return None
                            
                            payment = 0
                            new_balance = 0
                            while True:
                                cur.execute("SELECT amount FROM expense_details WHERE expense_id = ? AND username = ?;",(update,payer))
                                current_balance = float(cur.fetchone()[0])
                                
                                print("\nThe payer is:",payer)
                                print("Payer's current balance from this expense is:",current_balance)
                                payment = round(float(input("How much did he/she pay?: ")), 2)
                                
                                if(payment <= current_balance):
                                    new_balance = current_balance-payment
                                    print("\nPayment received!")
                                    break
                                else:
                                    print("Payment exceeds current balance!")
                            
                            if(new_balance == 0):
                                cur.execute("UPDATE expense_details SET amount = ?, paid = 'Paid' WHERE expense_id = ? AND username = ?;",(new_balance,update,payer,))
                                cur.execute("UPDATE expense SET balance = ?, status = 'Paid' WHERE expense_id = ?",(new_balance,update))
                            else:
                                cur.execute("UPDATE expense_details SET amount = ? WHERE expense_id = ? AND username = ?;",(new_balance,update,payer,))
                                
                            cur.execute("SELECT SUM(amount) FROM expense_details WHERE expense_id = ?;",(update,))
                            updated_balance = cur.fetchone()[0]
                            if(updated_balance == 0):
                                cur.execute("UPDATE expense SET balance = ?, status = 'Paid' WHERE expense_id = ?",(updated_balance,update))
                            else:
                                cur.execute("UPDATE expense SET balance = ? WHERE expense_id = ?",(updated_balance,update))
                            mydb.commit()
                            
                        else:
                            cur.execute("SELECT * FROM expense_details WHERE expense_id = ? AND paid = 'Not paid'",(update,))
                            if(cur.rowcount == 0):
                                print("Everyone involved has already paid for the expense!\n")
                                return None 
                            
                            result = cur.fetchall()
                            col_name = [description[0] for description in cur.description]
                            print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))
                            
                            payer = input("Who paid in the group expense?: ")
                            payment = 0
                            new_balance = 0
                            while True:
                                cur.execute("SELECT amount FROM expense_details WHERE expense_id = ? AND username = ?;",(update,payer))
                                current_balance = float(cur.fetchone()[0])
                                
                                print("\nThe payer is:",payer)
                                print("Payer's current balance from this expense is:",current_balance)
                                payment = round(float(input("How much did he/she pay?: ")), 2)

                                if(payment <= current_balance):
                                    new_balance = current_balance-payment
                                    print("\nPayment received!")
                                    break
                                else:
                                    print("Payment exceeds current balance!")

                            if(new_balance == 0):
                                cur.execute("UPDATE expense_details SET amount = ?, paid = 'Paid' WHERE expense_id = ? AND username = ?;",(new_balance,update,payer,))
                            else:
                                cur.execute("UPDATE expense_details SET amount = ? WHERE expense_id = ? AND username = ?;",(new_balance,update,payer,))
                               
                            cur.execute("SELECT SUM(amount) FROM expense_details WHERE expense_id = ?;",(update,))
                            updated_balance = cur.fetchone()[0]
                            if(updated_balance == 0):
                                cur.execute("UPDATE expense SET balance = ?, status = 'Paid' WHERE expense_id = ?",(updated_balance,update))
                            else:
                                cur.execute("UPDATE expense SET balance = ? WHERE expense_id = ?",(updated_balance,update))
                            mydb.commit()
                              
                    except ValueError:
                        print("Balance invalid!")
                        return None

                elif(attribute == 3):
                    value = input("New description: ")

                    if(len(value) > 30):
                        print("Description is too long!")
                        return None

                    cur.execute("UPDATE expense SET description_expense = ? WHERE expense_id = ?;",(value,update,))
                    mydb.commit()
                elif(attribute == 4):
                    break
                else:
                    print("Invalid input!")
        else:
            print("Expense ID ",update," does not exist.")

def add_friend(cur, mydb, current_user):
    friend_list = show_users_not_friend(cur, current_user)
    if(friend_list is not False):
        username = input("\nEnter username of user you want to add as a friend: ")

        if(username not in friend_list):
            print("Username is not part of the list of possible friends!")
            return None

        cur.execute("INSERT INTO user_friend VALUES (?,?);",(current_user,username,))    
        cur.execute("INSERT INTO user_friend VALUES (?,?);",(username,current_user,))
        mydb.commit()

        print("Successfully added friend!")

def delete_friend(cur, mydb, current_user):
    friend_list = show_users_friend(cur, current_user)
    if(friend_list is not False):
        username = input("\nEnter username of user you want to unfriend: ")

        if(username not in friend_list):
            print("Username is not part of your list of friends!")
            return None

        cur.execute("DELETE FROM user_friend WHERE username=? AND friend_username=?;",(current_user,username,)) 
        cur.execute("DELETE FROM user_friend WHERE username=? AND friend_username=?;",(username,current_user,))

        mydb.commit()

        print("Successfully unfriended!")

def search_friend(cur, current_user):
    friend_list = show_users_friend(cur, current_user)
    if(friend_list is not False):
        username = input("\nUsername of friend you want details of: ")

        if(username not in friend_list):
            print("Username is not part of your list of friends!")
            return None

        show_friend_details(cur, username)

def add_group(cur, mydb, current_user):
    cur.execute("SELECT username FROM user WHERE username=ANY(SELECT friend_username FROM user_friend WHERE username=?) AND NOT username=?;",(current_user, current_user,))
    friend_count = cur.rowcount 
    result = cur.fetchall()
    friend_list = [i[0] for i in result]
    
    if(friend_count <= 1):
        print("You do not have enough friends to form a group!")
    else:
        groupname = input("\nName of the group: ")

        cur.execute("SELECT group_name from friend_group;")
        result = cur.fetchall()
        groupname_list = [i[0] for i in result]
        
        if(groupname in groupname_list):
            print("Group name already exists!")
            return None
        
        if(len(groupname) > 20):
            print("Group name is too long!")
            return None

        try:
            n = int(input("Number of members: "))
            if(n<3):
                print("Number of members must be greater than 2 to be considered a group!")
                return None
            elif(n > (friend_count+1)):
                print("Number of members you inputted is more than the possible number of members given the current number of your friends!")
                return None
        except ValueError:
            print("Invalid number!")
            return None

        cur.execute("SELECT * FROM friend_group;")
        result = cur.fetchall()

        group_id = len(result)
        added = [current_user]
        count = 0
        while count < (n-1):
            show_users_friend(cur,current_user)
            member  = input("\nUsername of the user you want to add into the group: ")
            if(member not in added):
                if(member in users_list(cur) and member in friend_list):    #check if the user is existing
                    cur.execute("INSERT INTO group_details VALUES(?,?)",(member,group_id+1))
                    added.append(member)
                    count = count + 1
                else:
                    print("No user found.")
                    continue
            else:
                print("You have already added this username to this group!")
        
        cur.execute("INSERT INTO group_details VALUES(?,?)",(current_user,group_id+1)) #to simulate the automatic addition of the current user when creating a group    
        cur.execute("ALTER TABLE friend_group AUTO_INCREMENT=?;",(group_id,))
        cur.execute("INSERT INTO friend_group (group_name) VALUES (?);", (groupname,))
        mydb.commit()

        print("\nGroup successfully added!")

def delete_group(cur, mydb,current_user):
    result = show_groups(cur,current_user)
    if(result is not False):
        delete = int(input("\nGroup id of the expense that you want to delete: "))
        
        cur.execute("SELECT group_id FROM friend_group WHERE group_id IN (SELECT group_id FROM group_details WHERE username=?);",(current_user,))
        rows = cur.fetchall()
        groupid_list = [i[0] for i in rows]
        
        if(delete in groupid_list):
            cur.execute("DELETE FROM expense WHERE group_id=?;",(delete,))
            cur.execute("DELETE FROM group_details WHERE group_id=?;",(delete,))
            cur.execute("DELETE FROM friend_group WHERE group_id=?;",(delete,))
            mydb.commit()
            print("\nGroup successfully deleted!")
        else:
            print("You have inputted a non-existing group!")

def search_group(cur,current_user):
    result = show_groups(cur,current_user)
    if(result is not False):
        search = int(input("\nGroup id of the expense that you want details of: "))
        
        cur.execute("SELECT group_id FROM friend_group WHERE group_id IN (SELECT group_id FROM group_details WHERE username=?);",(current_user,))
        rows = cur.fetchall()
        groupid_list = [i[0] for i in rows]
        
        if(search in groupid_list):
            cur.execute("SELECT group_id, username FROM friend_group NATURAL JOIN group_details WHERE group_id = ? ORDER BY group_id;",(search,))
            result = cur.fetchall()
            col_name = [description[0] for description in cur.description]
            print("\nHere are the members of the group:")
            print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))
        else:
            print("You have inputted a non-existing group!")

def edit_group(cur, mydb,current_user):
    result = show_groups(cur,current_user)
    if(result is not False):
        update = int(input("\nGroup id of the group that you want to update: "))
        
        cur.execute("SELECT group_id FROM friend_group WHERE group_id IN (SELECT group_id FROM group_details WHERE username=?);",(current_user,))
        rows = cur.fetchall()
        groupid_list = [i[0] for i in rows]
        
        if(update in groupid_list):
            while True:
                print(dedent("""
                ======================
                      EDIT GROUP      
                ======================
                [1] Change group name
                [2] Edit members
                [3] Back
                ______________________
                """))
                try:
                    attribute = int(input("Enter choice [1-3]: "))
                except ValueError:
                    print("Invalid input!")
                    continue

                if(attribute == 1):
                    value = input("New value: ")

                    if(len(value) > 20):
                        print("Group name is too long!")
                        return None

                    cur.execute("UPDATE friend_group SET group_name = ? WHERE group_id = ?;",(value,update,))
                    mydb.commit()
                    
                elif(attribute == 2):
                    print(dedent("""
                    -----------
                    [1] Add
                    [2] Delete
                    -----------
                    """))
                    try:
                        choice = int(input("Enter choice [1-2]: "))
                    except ValueError:
                        print("Invalid input!")
                        continue

                    if(choice == 1):
                        cur.execute("SELECT username FROM user WHERE NOT username=ANY(SELECT username FROM user NATURAL JOIN group_details WHERE group_id=?);",(update,))
                        result = cur.fetchall()
                        user_list = [i[0] for i in result]
                        col_name = [description[0] for description in cur.description]
                        print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

                        member  = input("\nUsername of the user you want to add: ")
                        if(member in user_list):    #check if the user is existing
                            cur.execute("INSERT INTO group_details VALUES(?,?)",(member,update,))
                            print(member + " was successfully added!")
                            mydb.commit()
                        else:
                            print("No user found.")

                    elif(choice == 2):
                        cur.execute("SELECT u.username FROM user u JOIN group_details g ON u.username=g.username WHERE g.group_id=?;",(update,))
                        rows = cur.fetchall()
                        member_list = [i[0] for i in rows]

                        cur.execute("SELECT username FROM user NATURAL JOIN group_details WHERE group_id = ?;",(update,))
                        result = cur.fetchall()
                        col_name = [description[0] for description in cur.description]
                        print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

                        dmember  = input("\nUsername of the member you want to delete: ")
                        if(dmember in member_list):    #check if the user is existing
                            cur.execute("DELETE FROM group_details WHERE username=? AND group_id=?",(dmember,update,))
                            print(dmember + " was successfully deleted!")  
                            mydb.commit()
                        else:
                            print("User is not a member of the group.")
                    else:
                        print("Invalid input!")
                elif(attribute == 3):
                    break
                else:
                    print("Invalid input!")
        else:
            print("Group ID ",update," does not exist.")

# -- REPORT 1: View all expenses made within a month --
def view_monthexpense(cur):
    cur.execute("SELECT * FROM month_expense;")
    result = cur.fetchall()
    col_name = [description[0] for description in cur.description]
    
    print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

# -- REPORT 2: View all expenses made with a friend  --
def view_friendexpense(cur, current_user, friend):
    cur.execute("SELECT * FROM friend_expense;")
    if(cur.rowcount == 0):
        print("You have no expenses with",friend,".")
    else:
        result = cur.fetchall()
        col_name = [description[0] for description in cur.description]
    
        print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

# -- REPORT 3: View all expenses made with a group (where your group is friends) --
def view_groupexpense(cur):
    cur.execute("SELECT * FROM group_expense;")
    result = cur.fetchall()
    col_name = [description[0] for description in cur.description]
    
    print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

# -- REPORT 4: View current balance from all expenses --
def view_currentbalance(cur):
    cur.execute("SELECT * FROM current_balance")
    result = cur.fetchall()
    col_name = [description[0] for description in cur.description]
    
    print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

# -- REPORT 5: View all friends with outstanding balance --
def view_friendbalance(cur):
    cur.execute("SELECT * FROM friend_balance;")
    result = cur.fetchall()
    col_name = [description[0] for description in cur.description]
    
    print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))

# -- REPORT 6: View all groups --
def view_group(cur):
    cur.execute("SELECT * FROM all_group;")
    result = cur.fetchall()
    col_name = [description[0] for description in cur.description]
    
    print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))
    
# -- REPORT 7: View all groups with an outstanding balance --
def view_groupbalance(cur):
    cur.execute("SELECT * FROM group_balance;")
    result = cur.fetchall()
    col_name = [description[0] for description in cur.description]
    
    print(tabulate(result, headers=col_name, tablefmt = 'fancy_grid'))
    
def connect():
    # connect to the database
    try:
        mydb = mariadb.connect(
            user="expense_tracker",
            password="expense",
            host="localhost",
            port=3306,
            database="expense_tracker",
        )
        print("Connected to MariaDB!")
        
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Create cursor object
    cur = mydb.cursor()

    current_user = ""

    # logging in to an "account" or creating an account
    while True:
        print(dedent("""
        ------------------------------------------------------
        |                     WELCOME TO                     |
        ------------------------------------------------------

                                /$$     /$$     /$$          
                               | $$    | $$    | $$          
           /$$$$$$$  /$$$$$$  /$$$$$$ /$$$$$$  | $$  /$$$$$$ 
          /$$_____/ /$$__  $$|_  $$_/|_  $$_/  | $$ /$$__  $$
         |  $$$$$$ | $$$$$$$$  | $$    | $$    | $$| $$  \__/
          \____  $$| $$_____/  | $$ /$$| $$ /$$| $$| $$      
          /$$$$$$$/|  $$$$$$$  |  $$$$/|  $$$$/| $$| $$      
         |_______/  \_______/   \___/   \___/  |__/|__/      

                SPLIT AND SETTLE EXPENSES WITH FRIENDS        
        ______________________________________________________              
        """))
        print(dedent("""
        [1] Login
        [2] Create account
        [3] Exit
        """))
        try:
            choice = int(input("Enter choice [1-3]: "))
        except ValueError:
            print("Invalid input!")
            continue

        if(choice == 1):
            current_user = login(cur)

            if(current_user != None):
                app(cur, mydb, current_user)
        elif(choice == 2):
            current_user = signUp(cur, mydb)

            if(current_user != None):
                app(cur, mydb, current_user)
        elif(choice == 3):
            print("\nThank you for using Settlr!")
            print(dedent("""
            $$\                           
            $$ |                          
            $$$$$$$\  $$\   $$\  $$$$$$\  
            $$  __$$\ $$ |  $$ |$$  __$$\ 
            $$ |  $$ |$$ |  $$ |$$$$$$$$ |
            $$ |  $$ |$$ |  $$ |$$   ____|
            $$$$$$$  |\$$$$$$$ |\$$$$$$$\ 
            \_______/  \____$$ | \_______|
                      $$\   $$ |          
                      \$$$$$$  |          
                       \______/           
            """))
            break
        else: 
            print("Invalid input. Please make another input and make sure that it is correct!")

def app(cur, mydb, current_user):
    while True:
        print(dedent("""
        -----------------------
        |      MAIN MENU      |
        -----------------------
        [1] Edit profile
        [2] Expense
        [3] Friends
        [4] Group
        [5] Generate reports
        [6] Log out
        _______________________
        """))
        try:
            choice = int(input("Enter choice [1-6]: "))
        except ValueError:
            print("Invalid input!")
            continue

        if(choice == 1):
            edit_profile(cur, mydb, current_user)
        elif(choice == 2):
            expense(cur, mydb, current_user)
        elif(choice == 3):            
            friend(cur, mydb, current_user)
        elif(choice == 4):
            group(cur, mydb, current_user)
        elif(choice == 5):
            report(cur, current_user)
        elif(choice == 6):
            print("Thank you for using Settlr!")
            break
        else:
            print("Invalid input. Please make another input and make sure that it is correct!")

def expense(cur, mydb, current_user):
    while True:
        print(dedent("""
        -------------------------------
        |          EXPENSES           |
        -------------------------------
        [1] Add an expense
        [2] Delete an expense
        [3] Search for an expense
        [4] Update an expense
        [5] Back
        _______________________________
        """))
        try:
            choice = int(input("Enter choice [1-5]: "))
        except ValueError:
            print("Invalid input!")
            continue
        
        if(choice == 1):
            print(dedent("""
            Is it a group expense?
            [1] Yes
            [2] No
            """))

            group_expense = int(input("Enter choice [1-2]: "))

            if(group_expense == 1):
                add_group_expense(cur, mydb, current_user)
            elif(group_expense == 2):
                add_indiv_expense(cur, mydb, current_user)
        elif(choice == 2):
            delete_expense(cur, mydb, current_user)
        elif(choice == 3):
            search_expense(cur, current_user)
        elif(choice == 4):
            edit_expense(cur, mydb, current_user)
        elif(choice == 5):
            break
        else:
            print("Invalid input!")

def friend(cur, mydb, current_user):
    while True:
        print(dedent("""
        -------------------------------
        |           FRIENDS           |
        -------------------------------
        [1] Add a friend
        [2] Delete a friend
        [3] Search for friend
        [4] Back
        _______________________________
        """))
        try:
            choice = int(input("Enter choice [1-4]: "))
        except ValueError:
            print("Invalid input!")
            continue

        if(choice == 1):
            add_friend(cur, mydb, current_user)
        elif(choice == 2):
            delete_friend(cur, mydb, current_user)
        elif(choice == 3):
            search_friend(cur, current_user)
        elif(choice == 4):
            break
        else:
            print("Invalid input!")

def group(cur, mydb, current_user):
    while True:
        print(dedent("""
        -------------------------------
        |            GROUPS           |
        -------------------------------
        [1] Add a group
        [2] Delete a group
        [3] Search for a group
        [4] Update a group
        [5] Back
        _______________________________
        """))
        try:
            choice = int(input("Enter choice [1-5]: "))
        except ValueError:
            print("Invalid input!")
            continue
        
        if(choice == 1):
            add_group(cur, mydb, current_user)
        elif(choice == 2):
            delete_group(cur, mydb, current_user)
        elif(choice == 3):
            search_group(cur, current_user)
        elif(choice == 4):
            edit_group(cur, mydb, current_user)
        elif(choice == 5):
            break
        else:
            print("Invalid input!")

def report(cur, current_user):
    while True:
        print(dedent("""
        ------------------------------------------------
        |               GENERATE REPORTS               |
        ------------------------------------------------
        [1] View all expenses made within a month
        [2] View all expenses made with a friend
        [3] View all expenses made with a group
        [4] View current balance from all expenses
        [5] View all friends with outstanding balance
        [6] View all groups
        [7] View all groups with an outstanding balance
        [8] Back
        ________________________________________________
        """))
        choice = int(input("Enter choice [1-8]: "))
        
        if(choice == 1):
            cur.execute("SELECT * FROM expense WHERE (date_made BETWEEN ADDDATE(CURDATE(),INTERVAL -1 month) AND CURDATE()) AND individual_paid=?;",(current_user,))
            if(cur.rowcount == 0):
                print("You either have no recorded expenses yet or no recent expenses within the last month!")
            else:
                cur.execute("CREATE OR REPLACE VIEW month_expense AS SELECT * FROM expense WHERE (date_made BETWEEN ADDDATE(CURDATE(),INTERVAL -1 month) AND CURDATE()) AND individual_paid=?;",(current_user,))
                view_monthexpense(cur)
                
        elif(choice == 2):
            friend_list = show_users_friend(cur, current_user)
            friend = input("Username of friend: ")
            
            if (friend not in users_list(cur)):
                print("No user found.")
            elif (friend not in friend_list):
                print(friend, "is not your friend.")
            else: 
                cur.execute("CREATE OR REPLACE VIEW friend_expense AS SELECT * FROM expense WHERE (individual_paid=? AND username=?);",(current_user,friend,))
                view_friendexpense(cur,current_user,friend)
                
        elif(choice == 3):
            cur.execute("SELECT f.group_id FROM friend_group f LEFT JOIN group_details g ON f.group_id=g.group_id WHERE g.username=?;",(current_user,))
            rows = cur.fetchall()
            group_list = [i[0] for i in rows]
            result = show_groups(cur, current_user)

            if(result is not False):
                print("\nExpenses with what group?")
                group = int(input("Group ID: "))
                if(group in group_list):
                    cur.execute("CREATE OR REPLACE VIEW group_expense AS SELECT f.group_id,f.group_name,e.expense_id,status,balance,total_amount,description_expense,date_made,individual_paid FROM expense e NATURAL JOIN friend_group f WHERE e.group_id=f.group_id AND f.group_id=?;",(group,))
                    view_groupexpense(cur)
                else:
                    print("You're not a member of that group.")
                continue
            
        elif(choice == 4):
            cur.execute("SELECT * FROM current_balance WHERE expense_id IN (SELECT expense_id FROM expense_details WHERE username = ?);",(current_user,))
            if(cur.rowcount == 0):
                print("You have no expenses yet!")
            else:
                cur.execute("CREATE OR REPLACE VIEW current_balance AS SELECT expense_id,description_expense, balance FROM expense WHERE expense_id IN (SELECT expense_id FROM expense_details WHERE username = ?);",(current_user,))
                view_currentbalance(cur)
            
        elif(choice == 5):
            cur.execute("SELECT username FROM user WHERE username=ANY(SELECT friend_username FROM user_friend WHERE username=?) AND NOT username=?;",(current_user, current_user,))
            if(cur.rowcount == 0):
                print("You have no friends yet!")
            else:
                cur.execute("CREATE OR REPLACE VIEW friend_balance AS SELECT e.expense_id, e.description_expense, ed.username,ed.paid,ed.amount FROM expense e JOIN expense_details ed ON e.expense_id=ed.expense_id WHERE e.group_id IS NULL AND paid='Not paid' AND e.individual_paid=?;",(current_user,))
                view_friendbalance(cur)
                
        elif(choice == 6):
            cur.execute("SELECT * FROM friend_group WHERE group_id IN (SELECT group_id FROM group_details WHERE username=?);",(current_user,))
            if(cur.rowcount == 0):
                print("You are not part of any groups yet!")
            else:
                cur.execute("CREATE OR REPLACE VIEW all_group AS SELECT * FROM friend_group WHERE group_id IN (SELECT group_id FROM group_details WHERE username=?);",(current_user,))
                view_group(cur)
    
        elif(choice == 7):
            cur.execute("SELECT * FROM friend_group WHERE group_id IN (SELECT group_id FROM group_details WHERE username=?);",(current_user,))
            if(cur.rowcount == 0):
                print("You are not part of any groups yet!")
            else:
                cur.execute("CREATE OR REPLACE VIEW group_balance AS SELECT group_name, description_expense, balance FROM expense e NATURAL JOIN friend_group fg WHERE status='Not paid' AND e.group_id IN (SELECT group_id FROM group_details WHERE username=?);",(current_user,))
                view_groupbalance(cur)
                
        elif(choice == 8):
            break
        else:
            print("Invalid input!")

connect()
