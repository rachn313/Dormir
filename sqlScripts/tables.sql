drop table if exists Reviews;
drop table if exists Users;

create table Users(
       uid int auto_increment,
       fullname varchar(50) not null,
       biotxt varchar(350),
       profpicPath varchar(50),
       primary key (uid)
);


create table Reviews(
    rid int auto_increment not null primary key,
    rmID varchar(10),
    rating enum("1", "2", "3", "4", "5"),
    review varchar(500),
    imgPath varchar(50), 
    time timestamp
   
);

-- enter data
-----source enter-users.sql;
--source enter-reviews.sql;

 -- foreign key (uid) references Users(uid)
    --       on delete cascade        
   -- uid int,



