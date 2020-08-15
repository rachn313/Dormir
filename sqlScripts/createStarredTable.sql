drop table if exists Starred;
create table Starred(
       uid int, 
       rmID varchar(10),
       primary key (uid, rmID),
       foreign key (uid) references users(uid)
       	on delete cascade

);