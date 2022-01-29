/*
Not in table = Timeout mode
In table = Ban mode
*/
create table if not exists modes(
    guild integer primary key
);

create table if not exists periods(
    guild integer primary key,
    days integer not null check(days >= 1 and days <= 28)
);

create table if not exists punishments(
    guild integer primary key,
    count integer not null check(count > 0)
);

create table if not exists logs(
    guild integer primary key,
    channel integer not null
);
