CREATE TABLE players(
    server varchar(10),
    summonerId varchar(50),
    accountId varchar(50),
    puuid varchar(50),
    PRIMARY KEY (server, summonerId)
);

CREATE TABLE matches(
    server varchar(50),
    id varchar(50),
    fetched boolean,
    notFetched boolean,
    discarded boolean,
    PRIMARY KEY (server, id)
);

CREATE TABLE comps(
    id varchar(50),
    place int,
    trait1 varchar(10),
    trait2 varchar(10),
    trait3 varchar(10),
    trait4 varchar(10),
    trait5 varchar(10),
    trait6 varchar(10),
    trait7 varchar(10),
    trait8 varchar(10),
    chmap1 varchar(10),
    chmap2 varchar(10),
    chmap3 varchar(10),
    chmap4 varchar(10),
    chmap5 varchar(10),
    chmap6 varchar(10),
    chmap7 varchar(10),
    chmap8 varchar(10),
    chmap9 varchar(10),
    chmap10 varchar(10),
    augment1 varchar(10),
    augment2 varchar(10),
    augment3 varchar(10),
    PRIMARY KEY(id, place),
    FOREIGN KEY (id) REFERENCES matches(id)
);

CREATE TABLE champs(
    id varchar(50),
    place int,
    champID varchar(10),
    item1 varchar(10),
    item2 varchar(10),
    item3 varchar(10),
    FOREIGN KEY (id,place) REFERENCES comps(id,place)
);