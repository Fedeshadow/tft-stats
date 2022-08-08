CREATE TABLE player(
    server varchar(10),
    playerId varchar(20),
    puuid varchar(20),
    PRIMARY KEY (server, playerId)
);

CREATE TABLE matches(
    server varchar(20),
    id varchar(20),
    fetched boolean,
    notFetched boolean,
    discarded boolean,
    PRIMARY KEY (server, id)
);

CREATE TABLE comps(
    id varchar(20),
    place int,
    trait1 varchar(10),
    trait2 varchar(10),
    trait3 varchar(10),
    trait4 varchar(10),
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
    id varchar(20),
    place int,
    champID varchar(10),
    item1 varchar(10),
    item2 varchar(10),
    item3 varchar(10),
    FOREIGN KEY (id,place) REFERENCES comps(id,place)
);