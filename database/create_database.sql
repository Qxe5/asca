/*
Not in table = Timeout mode
In table = Ban mode
*/
create table modes(
    guild integer primary key
);

create table punishments(
    guild integer primary key,
    count integer not null check(count > 0)
);

create table logs(
    guild integer primary key,
    channel integer not null
);
