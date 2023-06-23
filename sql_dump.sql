-- DCL -- 
--in root
CREATE USER expense_tracker IDENTIFIED BY 'expense';
CREATE DATABASE expense_tracker;
GRANT ALL PRIVILEGES ON expense_tracker.* TO expense_tracker;

-- DDL --
--in expense tracker
use expense_tracker;

CREATE TABLE user(
    username VARCHAR(20) NOT NULL,
    email VARCHAR(30) NOT NULL,
    name VARCHAR(30) NOT NULL,
    password VARCHAR(10) NOT NULL,
    CONSTRAINT user_username_pk PRIMARY KEY(username)
);

CREATE TABLE friend_group(
    group_id INT(3) NOT NULL AUTO_INCREMENT,
    group_name VARCHAR(20) NOT NULL,
    CONSTRAINT group_group_id_pk PRIMARY KEY(group_id)
);

CREATE TABLE expense(
    expense_id INT(3) NOT NULL AUTO_INCREMENT,
    status ENUM('Not paid','Paid') NOT NULL,
    balance DECIMAL(6,2) NOT NULL, 
    total_amount DECIMAL(6,2) NOT NULL,
    description_expense VARCHAR(30),
    date_made DATE DEFAULT CURDATE() NOT NULL,
    individual_paid VARCHAR(20) NOT NULL,
    username VARCHAR(20) DEFAULT NULL,
    group_id INT(3) DEFAULT NULL,
    CONSTRAINT expense_expense_id_pk PRIMARY KEY(expense_id),
    CONSTRAINT expense_username_fk FOREIGN KEY(username) REFERENCES user(username),
    CONSTRAINT expense_group_id_fk FOREIGN KEY(group_id) REFERENCES friend_group(group_id)
);

CREATE TABLE expense_details(
	username VARCHAR(20) NOT NULL,
    expense_id INT(3) NOT NULL,
    paid ENUM('Not paid','Paid') DEFAULT NULL, -- possible solution to keep track of individual balances in a group expense
    amount DECIMAL(6,2) DEFAULT NULL,
	CONSTRAINT expense_details_username_expense_id_uk UNIQUE(username, expense_id)
);

CREATE TABLE group_details(
    username VARCHAR(20) NOT NULL,
    group_id INT(3) NOT NULL,
	CONSTRAINT group_details_username_group_id_uk UNIQUE(username, group_id)
);

CREATE TABLE user_friend(
	username VARCHAR(20) NOT NULL,
	friend_username VARCHAR(20) NOT NULL,
	CONSTRAINT user_friend_username_friend_username_uk UNIQUE(username, friend_username)
);


-- DML --
-- USERS --
INSERT INTO user VALUES
	("rgreen", "rgreen@gmail.com", "Rachel Green", "rachel"),
	("pbuffay", "pbuffay@gmail.com", "Phoebe Buffay", "phoebe"), 
    ("rgeller", "rgeller@gmail.com", "Ross Geller", "ross"),
    ("mgeller", "mgeller@gmail.com", "Monica Geller", "monica"),
    ("cbing", "cbing@gmail.com", "Chandler Bing", "chandler"),
    ("jtribbiani", "jtribbiani@gmail.com", "Joey Tribbiani", "joey"),
    ("scooper", "scooper@gmail.com", "Sheldon Cooper", "sheldon"),
    ("lhofstader", "lhofstader@gmail.com", "Leonard Hofstader", "leonard"),
    ("hwolowitz", "hwolowitz@gmail.com", "Howard Wolowitz", "howard"),
    ("rkoothrappali","rkoothrappali@gmail.com", "Raj Koothrappali", "raj");
    
-- FRIEND GROUPS --
INSERT INTO friend_group VALUES (1, "Friends"), (2, "TBBT");

-- GROUP DETAILS --
INSERT INTO group_details VALUES
	("rgreen", 1),
	("pbuffay", 1),
	("rgeller", 1),
	("mgeller", 1),
	("cbing", 1),
	("jtribbiani", 1),
	("scooper", 2),
	("lhofstader", 2),
	("hwolowitz", 2),
	("rkoothrappali", 2);
   
-- EXPENSES --
INSERT INTO expense VALUES
	(1, "Not paid", 100.00, 600.00, "Lunch in Central Perk", str_to_date('10-MAY-2023','%d-%M-%Y'), "rgeller", NULL, 1),
	(2, "Paid", 0.00, 400.00, "Dinner in Cheesecake Factory", str_to_date('03-MAR-2023','%d-%M-%Y'), "lhofstader", NULL, 2),
	(3, "Paid", 0.00, 200.00, "Wedding dinner", str_to_date('10-MAY-2023','%d-%M-%Y'), "cbing", "mgeller", NULL),
	(4, "Not paid", 100.00, 200.00, "Knicks game", str_to_date('02-FEB-2023','%d-%M-%Y'), "cbing", "jtribbiani", NULL),
	(5, "Not paid", 100.00, 600.00, "Phoebe birthday", str_to_date('06-MAY-2023','%d-%M-%Y'), "pbuffay", NULL, 1);
	
-- EXPENSE DETAILS --
INSERT INTO expense_details VALUES
	("rgreen", 1, "Paid", 0.00),
	("pbuffay", 1, "Paid", 0.00),
    ("rgeller", 1, "Paid", 0.00),
    ("mgeller", 1, "Not paid", 100.00),
    ("cbing", 1, "Paid", 0.00),
    ("jtribbiani", 1, "Paid", 0.00),
    ("lhofstader", 2, "Paid", 0.00),
    ("scooper", 2, "Paid", 0.00),
    ("hwolowitz", 2, "Paid", 0.00),
    ("rkoothrappali", 2, "Paid", 0.00),
    ("rgreen", 5, "Paid", 0.00),
	("pbuffay", 5, "Paid", 0.00),
    ("rgeller", 5, "Paid", 0.00),
    ("mgeller", 5, "Not paid", 100.00),
    ("cbing", 5, "Paid", 0.00),
    ("jtribbiani", 5, "Paid", 0.00),
    ("jtribbiani", 4, "Not paid", 100.00),
	("cbing", 4, "Paid", 100.00),
	("cbing", 3, "Paid", 100.00),
    ("mgeller", 3, "Paid", 0.00);
    
-- FRIENDS --
INSERT INTO user_friend VALUES
	("rgreen", "pbuffay"),
	("rgreen", "rgeller"),
	("rgreen", "mgeller"),
	("rgreen", "cbing"),
	("rgreen", "jtribbiani"),
	("pbuffay", "rgreen"),
	("pbuffay", "rgeller"),
	("pbuffay", "mgeller"),
	("pbuffay", "cbing"),
	("pbuffay", "jtribbiani"),
	("rgeller", "rgreen"),
	("rgeller", "pbuffay"),
	("rgeller", "mgeller"),
	("rgeller", "cbing"),
	("rgeller", "jtribbiani"),
	("mgeller", "rgreen"),
	("mgeller", "pbuffay"),
	("mgeller", "rgeller"),
	("mgeller", "cbing"),
	("mgeller", "jtribbiani"),
	("cbing", "rgreen"),
	("cbing", "pbuffay"),
	("cbing", "rgeller"),
	("cbing", "mgeller"),
	("cbing", "jtribbiani"),
	("jtribbiani", "rgreen"),
	("jtribbiani", "pbuffay"),
	("jtribbiani", "rgeller"),
	("jtribbiani", "mgeller"),
	("jtribbiani", "cbing"),
	("scooper", "lhofstader"),
	("scooper", "hwolowitz"),
	("scooper", "rkoothrappali"),
	("lhofstader", "scooper"),
	("lhofstader", "hwolowitz"),
	("lhofstader", "rkoothrappali"),
	("hwolowitz", "scooper"),
	("hwolowitz", "lhofstader"),
	("hwolowitz", "rkoothrappali"),
	("rkoothrappali", "scooper"),
	("rkoothrappali", "lhofstader"),
	("rkoothrappali", "hwolowitz");
	
-- REPORT 1: View all expenses made within a month --
CREATE VIEW month_expense AS SELECT * FROM expense WHERE date_made BETWEEN ADDDATE(CURDATE(),INTERVAL -1 month) AND CURDATE();
SELECT * FROM month_expense;

-- REPORT 2: View all expenses made with a friend (where you are logged in as chandler and your friend is monica) --
CREATE VIEW friend_expense AS SELECT * FROM expense WHERE ((individual_paid="cbing" AND username="mgeller")); --assuming the indiv paid is always the current user
SELECT * FROM friend_expense;

-- REPORT 3: View all expenses made with a group (where your group is friends) --
CREATE VIEW group_expense AS SELECT * FROM expense e NATURAL JOIN friend_group f WHERE e.group_id=f.group_id AND f.group_name="Friends";
SELECT * FROM group_expense;

-- REPORT 4: View current balance from all expenses --
CREATE VIEW current_balance AS SELECT expense_id,description_expense, balance FROM expense;
SELECT * FROM current_balance;

-- REPORT 5: View all friends with outstanding balance --
CREATE VIEW friend_balance AS SELECT e.expense_id, e.description_expense, ed.username,ed.paid,ed.amount FROM expense e JOIN expense_details ed ON e.expense_id=ed.expense_id WHERE e.group_id IS NULL AND paid="Not paid";
SELECT * FROM friend_balance;

-- REPORT 6: View all groups --
CREATE VIEW all_group AS SELECT * FROM friend_group;
SELECT * FROM all_group;

-- REPORT 7: View all groups with an outstanding balance --
CREATE VIEW group_balance AS SELECT group_name, description_expense, balance FROM expense e NATURAL JOIN friend_group f WHERE e.group_id=f.group_id AND status="Not paid";
SELECT * FROM group_balance;

/* ASSUMPTIONS
1. If null yung username, ibig sabihin group expense siya. If null yung group_id, ibig sabihin expense lang siya between the one who paid and his/her friend
2. EXPENSE:
	- status: whether the entire expense has been paid off (if paid off, the balance will be 0. if not, then someone from expense_details hasn't paid yet)
    - balance: how much hasn't been paid
    - total_amount: total amount of the expense
    - individual_paid: person who paid expense
    - username: person who has utang if it's a two person expense
    - group_id: shows the group that the expense is split with if it's split by group. this will determine how many are part of the expense, and how many the total amount will be divided into.
3. EXPENSE DETAILS:
	- username: person that's part of the expense
	- expense_id: expense they're part of
    - paid: whether they've paid or not
    - amount: how much they should pay (expense.total_amount / number of group members in expense.group_id for group expenses, expense.total_amount / 2 for pair expenses)
   
   Each member of the group (if an expense is made within that group) will be listed in expense_details. Expenses made with two people are also listed in expense_details.
*/
