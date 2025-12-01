DROP TABLE IF EXISTS ville, station, mois, annee, modele, categorie, consomme, parcours, possede, se_ravitaille, controle_technique, probleme, maintenance, reservoir, bus, entreprise;


CREATE TABLE ville(
  id_ville INT AUTO_INCREMENT,
  nom_ville VARCHAR(255),
    PRIMARY KEY (id_ville)
);

CREATE TABLE station(
  id_station INT AUTO_INCREMENT,
  nom_station VARCHAR(255),
    PRIMARY KEY (id_station)
);

CREATE TABLE mois(
  id_mois INT AUTO_INCREMENT,
    libelle_mois VARCHAR(255),
    PRIMARY KEY (id_mois)
);

CREATE TABLE modele(
  id_modele INT AUTO_INCREMENT,
  capacite_stockage DECIMAL,
    pression DECIMAL,
    PRIMARY KEY (id_modele)
);

CREATE TABLE categorie(
    id_categorie INT AUTO_INCREMENT,
    libelle_categorie VARCHAR(255),
    PRIMARY KEY (id_categorie)
);

CREATE TABLE entreprise(
  id_entreprise INT AUTO_INCREMENT,
  nom_entreprise VARCHAR(255),
  ville_id INT,
  PRIMARY KEY (id_entreprise),
  CONSTRAINT fk_ville_id FOREIGN KEY (ville_id) REFERENCES ville(id_ville)
);

CREATE TABLE bus(
  id_bus INT AUTO_INCREMENT,
  poids DECIMAL,
  nb_passager INT,
  date_achat DATE,
  entreprise_id INT,
  PRIMARY KEY (id_bus),
  CONSTRAINT fk_entreprise_id FOREIGN KEY (entreprise_id) REFERENCES entreprise(id_entreprise)
);

CREATE TABLE controle_technique(
    id_ctrl_technique INT AUTO_INCREMENT,
  date_controle_technique DATE,
  kilometrage DECIMAL,
  bus_id INT,
  PRIMARY KEY (id_ctrl_technique),
  CONSTRAINT fk_bus_id FOREIGN KEY (bus_id) REFERENCES bus(id_bus)
);

CREATE TABLE reservoir(
  id_reservoir INT AUTO_INCREMENT,
  libelle_reservoir VARCHAR(255),
    date_installation DATE,
    volume DECIMAL,
  entreprise_id_reservoir INT,
  modele_id INT,
  PRIMARY KEY (id_reservoir),
  CONSTRAINT fk_entreprise_id_reservoir FOREIGN KEY (entreprise_id_reservoir) REFERENCES entreprise(id_entreprise),
    CONSTRAINT fk_modele_id FOREIGN KEY (modele_id) REFERENCES modele(id_modele)
);

CREATE TABLE maintenance(
  id_maintenance INT AUTO_INCREMENT,
  date_revision DATE,
  descriptif VARCHAR(255),
  reservoir_id INT,
  PRIMARY KEY (id_maintenance),
  CONSTRAINT fk_reservoir_id FOREIGN KEY (reservoir_id) REFERENCES reservoir(id_reservoir)
);

CREATE TABLE probleme(
    id_probleme INT AUTO_INCREMENT,
    descriptif_probleme VARCHAR(255),
    date_probleme DATE,
    duree_maintenance INT,
    categorie_id INT,
    maintenance_id INT,
    PRIMARY KEY (id_probleme),
    CONSTRAINT fk_categorie_id FOREIGN KEY (categorie_id) REFERENCES categorie(id_categorie),
    CONSTRAINT fk_maintenance_id FOREIGN KEY (maintenance_id) REFERENCES maintenance(id_maintenance)
);

CREATE TABLE se_ravitaille(
  bus_id_ravitaille INT,
  station_id_ravitaille INT,
  jj_mm_aaaa DATE,
  quantite DECIMAL,
  PRIMARY KEY (bus_id_ravitaille,station_id_ravitaille,jj_mm_aaaa),
  CONSTRAINT fk_bus_id_ravitaille FOREIGN KEY (bus_id_ravitaille) REFERENCES bus(id_bus),
    CONSTRAINT fk_station_id_ravitaille FOREIGN KEY (station_id_ravitaille) REFERENCES station(id_station)
);

CREATE TABLE possede(
  bus_id_possede INT,
  reservoir_id_possede INT,
  date_installe DATE,
    PRIMARY KEY (bus_id_possede,reservoir_id_possede),
    CONSTRAINT fk_bus_id_possede FOREIGN KEY (bus_id_possede) REFERENCES bus(id_bus),
    CONSTRAINT fk_reservoir_id_possede FOREIGN KEY (reservoir_id_possede) REFERENCES reservoir(id_reservoir)
);

CREATE TABLE parcours(
  bus_id_parcours INT,
  mois_id INT,
  nb_kilometre_parcourus DECIMAL,
    PRIMARY KEY (bus_id_parcours,mois_id),
    CONSTRAINT fk_bus_id_parcours FOREIGN KEY (bus_id_parcours) REFERENCES bus(id_bus),
    CONSTRAINT fk_mois_id FOREIGN KEY (mois_id) REFERENCES mois(id_mois)
);

CREATE TABLE consomme(
    bus_id_consomme     INT,
    annee_id            INT,
    consommation_annuel DECIMAL,
    PRIMARY KEY (bus_id_consomme, annee_id),
    CONSTRAINT fk_bus_id_consomme FOREIGN KEY (bus_id_consomme) REFERENCES bus (id_bus)
);


INSERT INTO ville (nom_ville) VALUES ('Paris'),
                                     ('Montbéliard');

INSERT INTO station (nom_station) VALUES ('Station Nord Paris'),
                                         ('Station Sud Paris'),
                                         ('Station Comte Est Montbe');

INSERT INTO mois (libelle_mois) VALUES ('Janvier'),
                                       ('Février'),
                                       ('Mars');

INSERT INTO modele (capacite_stockage, pression) VALUES (200.0, 250.0),
                                                        (300.0, 300.0);

INSERT INTO categorie (libelle_categorie) VALUES ('Mécanique'),
                                                 ('Électrique');

INSERT INTO entreprise (nom_entreprise, ville_id) VALUES ('HydroParis', 1),
                                                         ('Monthydro',2);

INSERT INTO bus (poids, nb_passager, date_achat, entreprise_id)
VALUES (8000, 50, '2020-01-10', 1),
       (8100, 55, '2021-03-20', 1),
       (8200, 60, '2022-06-10', 1),
       (8150,65,'2025-08-11',2),
       (6950,40,'2024-04-17',2),
       (7500,45,'2023-12-25',2);

INSERT INTO controle_technique (date_controle_technique, kilometrage, bus_id)
VALUES ('2024-01-10', 50000, 1),
       ('2024-02-15', 48000, 2),
       ('2024-03-05', 30000, 3),
       ('2025-11-24',245789,4),
       ('2024-12-31',10000,5),
       ('2025-02-12',398675,6);

INSERT INTO reservoir (libelle_reservoir, entreprise_id_reservoir, modele_id)
VALUES ('HydroMax', 1, 1),
       ('EcoFuel', 1, 2),
       ('MegaTank', 1, 1);

INSERT INTO maintenance (date_revision, descriptif, reservoir_id)
VALUES ('2024-02-01', 'Révision annuelle', 1),
       ('2024-03-01', 'Remplacement soupape', 2),
       ('2024-04-01', 'Nettoyage complet', 3);

INSERT INTO probleme (descriptif_probleme, date_probleme,duree_maintenance, categorie_id)
VALUES ('Fuite de pression', '2024-12-30',45, 1, ),
       ('Capteur défectueux','2025-10-29',7, 2, ),
       ('Joint usé','2025-03-18',4, 1, );

INSERT INTO se_ravitaille (bus_id_ravitaille, station_id_ravitaille, jj_mm_aaaa, quantite)
VALUES (1, 1, '2024-01-05', 120.5),
       (1, 2, '2024-02-06', 140.0),
       (2, 1, '2024-03-07', 130.0),
       (3, 2, '2024-03-20', 150.0),
       (4,3,'2025-11-23',125.3),
       (5,3,'2025-10-24',110.0),
       (6,3,'2025-11-19',121.3);

INSERT INTO possede (bus_id_possede, reservoir_id_possede, date_installe)
VALUES (1, 1, '2020-01-15'),
       (2, 2, '2021-03-20'),
       (3, 3, '2022-06-10'),
       (4, 1, '2025-06-10'),
       (5, 3, '2024-06-10'),
       (6, 2, '2023-06-10');

INSERT INTO parcours (bus_id_parcours, mois_id, nb_kilometre_parcourus)
VALUES (1, 1, 1553.0),
       (1, 2, 1767.0),
       (2, 1, 1332.0),
       (2, 2, 1630.0),
       (3, 1, 1299.0),
       (3, 2, 1578.0),
       (4, 2, 1778.0),
       (5, 1, 1478.0),
       (6, 3, 1878.0);

INSERT INTO consomme (bus_id_consomme, annee_id, consommation_annuel)
VALUES (1, 2024, 2500.0),
       (2, 2024, 2398.0),
       (3, 2024, 2423.0),
       (1,2025,1245.0),
       (1,2023,2678.9),
       (2,2025,2376.0),
       (4,2025,1276.0),
       (5,2025,2576.0),
       (6,2024,3376.0);


SELECT e.nom_entreprise,AVG(c.consommation_annuel) AS consommation_moyenne
FROM consomme c
JOIN bus b ON b.id_bus = c.bus_id_consomme
JOIN entreprise e ON e.id_entreprise = b.entreprise_id
GROUP BY e.nom_entreprise;

SELECT b.id_bus,m.libelle_mois AS mois,p.nb_kilometre_parcourus AS km_mensuel
FROM parcours p
JOIN mois m ON m.id_mois = p.mois_id
JOIN bus b ON b.id_bus = p.bus_id_parcours
ORDER BY b.id_bus, m.id_mois;


SELECT c.libelle_categorie,COUNT(p.id_probleme) AS nb_problemes
FROM probleme p
JOIN categorie c ON c.id_categorie = p.categorie_id
GROUP BY c.libelle_categorie;

