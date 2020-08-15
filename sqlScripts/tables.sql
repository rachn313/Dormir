drop table if exists Starred;
drop table if exists Reviews;
drop table if exists Users;

create table Users(
       uid int auto_increment,
       fullname varchar(50) not null,
       username varchar(20) not null,
       profpicPath varchar(50),
       unique(username),
       index(username),
       primary key (uid)
);


create table Reviews(
    rid int auto_increment not null primary key,
    uid int,
    rmID varchar(10),
    rating enum("1", "2", "3", "4", "5"),
    review varchar(500),
    imgPath varchar(50), 
    time timestamp,
    foreign key (uid) references Users(uid)
           on delete cascade   
);

create table Starred(
  uid int not null primary key,
  rmID varchar(10),
  foreign key (uid) references Users(uid)
   on delete cascade

);

<<<<<<< HEAD
-- -- enter data
-- source enter-users.sql;
-- source enter-reviews.sql;
=======
-- enter data
-----source enter-users.sql;
--source enter-reviews.sql;
>>>>>>> b10eb52a57c9eb7e263cec73c2e6733dcd2fd1af

 -- foreign key (uid) references Users(uid)
    --       on delete cascade        
   -- uid int,



