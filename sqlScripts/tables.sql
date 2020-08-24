drop table if exists Saves;
drop table if exists Reviews;
drop table if exists Users;

create table Users(
       uid int auto_increment,
       fullname varchar(50) not null,
       username varchar(20) not null,
       profpicPath varchar(50) default 'img/default_profilepic.jpg',
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

create table Saves(
  rmID varchar(10),
  uid int,
  primary key (uid, rmID),
  foreign key (uid) references Users(uid)
   on delete cascade
);

-- enter data
-----source enter-users.sql;
--source enter-reviews.sql;

 -- foreign key (uid) references Users(uid)
    --       on delete cascade        
   -- uid int,



