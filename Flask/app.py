#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Flask, request, render_template, redirect, flash

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = 'une cle(token) : grain de sel(any random string)'

                                    ## à ajouter
from flask import session, g
import pymysql.cursors

def get_db():
    if 'db' not in g:
        g.db =  pymysql.connect(
            host="localhost",                 # à modifier
            user="lbornert",                     # à modifier
            password="mon_mot_de_passe",                # à modifier
            database="BDDDTP",        # à modifier
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        # à activer sur les machines personnelles :
        activate_db_options(g.db)
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def activate_db_options(db):
    cursor = db.cursor()
    # Vérifier et activer l'option ONLY_FULL_GROUP_BY si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'sql_mode'")
    result = cursor.fetchone()
    if result:
        modes = result['Value'].split(',')
        if 'ONLY_FULL_GROUP_BY' not in modes:
            print('MYSQL : il manque le mode ONLY_FULL_GROUP_BY')   # mettre en commentaire
            cursor.execute("SET sql_mode=(SELECT CONCAT(@@sql_mode, ',ONLY_FULL_GROUP_BY'))")
            db.commit()
        else:
            print('MYSQL : mode ONLY_FULL_GROUP_BY  ok')   # mettre en commentaire
    # Vérifier et activer l'option lower_case_table_names si nécessaire
    cursor.execute("SHOW VARIABLES LIKE 'lower_case_table_names'")
    result = cursor.fetchone()
    if result:
        if result['Value'] != '0':
            print('MYSQL : valeur de la variable globale lower_case_table_names differente de 0')   # mettre en commentaire
            # cursor.execute("SET GLOBAL lower_case_table_names = 0")
            db.commit()
        else :
            print('MYSQL : variable globale lower_case_table_names=0  ok')    # mettre en commentaire
    cursor.close()


@app.route('/')
def show_accueil():
    return render_template('layout.html')


# ########################################### Ctrl Technique

@app.route('/ctrl-technique/show', methods=['GET'])
def show_ctrl_technique():
    mycursor = get_db().cursor()
    sql = '''  SELECT id_ctrl_technique AS id, date_controle_technique AS date_control, kilometrage, bus_id, date_achat,poids,nom_entreprise AS nom
        FROM controle_technique
        JOIN bus ON bus.id_bus = controle_technique.bus_id
        JOIN entreprise ON entreprise.id_entreprise = bus.entreprise_id
        ORDER BY date_controle_technique
         '''
    mycursor.execute(sql)

    liste_control = mycursor.fetchall()
    return render_template('ctrl_technique/show_ctrl_technique.html', ctrlTechnique=liste_control)


@app.route('/ctrl-technique/add', methods=['GET'])
def add_ctrl_technique():
    print('''affichage du formulaire pour saisir un controle technique''')
    mycursor = get_db().cursor()
    sql = '''   SELECT id_bus AS id
                FROM bus'''
    mycursor.execute(sql)

    type_ctrl = mycursor.fetchall()
    return render_template('ctrl_technique/add_ctrl_technique.html', bus=type_ctrl)

@app.route('/ctrl-technique/add',methods=['POST'])
def valid_add_ctrl_technique():
    dateCtrlTechnique=request.form.get('dateCtrlTechnique','')
    kilometrage=request.form.get('kilometrage','')
    bus_id=request.form.get('bus_id','')

    message = u'controle ajouté , dateCtrlTechnique : ' + dateCtrlTechnique + ' kilometrage: ' + str(kilometrage) + ' bus_id: ' + str(bus_id)
    print(message)

    mycursor = get_db().cursor()
    tuple_param = (dateCtrlTechnique, kilometrage, bus_id)
    sql = '''
          INSERT INTO controle_technique(id_ctrl_technique,date_controle_technique,kilometrage,bus_id)
          VALUES (NULL, %s, %s, %s); \
          '''
    print(sql, tuple_param)
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    flash(message, 'alert-success')
    return redirect('/ctrl-technique/show')


@app.route('/ctrl-technique/edit', methods=['GET'])
def edit_ctrl_technique():
    print('''affichage du formulaire pour modifier un controle technique''')
    print(request.args.get('id'))
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = '''   SELECT id_ctrl_technique, \
                       date_controle_technique         AS dateCtrlTechnique, \
                       kilometrage,
                       bus_id
                FROM controle_technique
                WHERE id_ctrl_technique= %s;      '''
    mycursor.execute(sql, (id,))
    ctrlTechnique = mycursor.fetchone()

    sql = '''   SELECT id_bus AS id
                FROM bus '''
    mycursor.execute(sql)
    bus = mycursor.fetchall()

    return render_template('ctrl_technique/edit_ctrl_technique.html', ctrlTechnique=ctrlTechnique, bus=bus)


@app.route('/ctrl-technique/edit', methods=['POST'])
def valid_edit_ctrl_technique():
    print('''modification de la salle''')
    id = request.form.get('id', '')
    dateCtrlTechnique = request.form.get('dateCtrlTechnique', '')
    kilometrage = request.form.get('kilometrage', '')
    bus_id = request.form.get('bus_id', '')
    message = u'type ajouté , id: ' + id + ' dateCtrlTechnique: ' + dateCtrlTechnique + ' kilometrage: ' + kilometrage + ' bus_id: ' + bus_id
    print(message)

    tuple_param = (dateCtrlTechnique, kilometrage, bus_id,id)
    mycursor = get_db().cursor()
    sql = '''
          UPDATE controle_technique
          SET date_controle_technique= %s, \
              kilometrage= %s, \
              bus_id= %s
          WHERE id_ctrl_technique = %s;'''
    mycursor.execute(sql, tuple_param)

    get_db().commit()

    flash(message, 'alert-success')
    return redirect('/ctrl-technique/show')


@app.route('/ctrl-technique/delete', methods=['GET'])
def delete_ctrl_technique():
    print('''suppression d'un controle technique''')
    print(request.args)
    print(request.args.get('id'))
    id = request.args.get('id')

    tuple_param = (id)
    mycursor = get_db().cursor()
    sql = '''DELETE \
             FROM controle_technique \
             WHERE id_ctrl_technique = %s; \
          '''
    mycursor.execute(sql, tuple_param)

    get_db().commit()

    message = u'un controle a été supprimé, id : ' + id
    print(message)
    flash(message, 'alert-warning')
    return redirect('/ctrl-technique/show')


@app.route('/etat/ctrl-technique', methods=['GET'])
def etat_ctrl_technique():
    mycursor = get_db().cursor()

    # stats global des controles techniques
    sql= '''
                         SELECT COUNT(DISTINCT ct.id_ctrl_technique) AS total_controles,
                                COUNT(DISTINCT ct.bus_id) AS nb_bus_controles,
                                AVG(ct.kilometrage) AS kilometrage_moyen,
                                MAX(ct.kilometrage) AS kilometrage_max,
                                MIN(ct.kilometrage) AS kilometrage_min,
                                MAX(ct.date_controle_technique) AS dernier_controle,
                                MIN(ct.date_controle_technique) AS premier_controle
                         FROM controle_technique ct
                         '''
    mycursor.execute(sql)
    stats_globales = mycursor.fetchone()

    # stats par entreprise
    sql = '''
                           SELECT e.nom_entreprise,COUNT(ct.id_ctrl_technique) AS nb_controles,AVG(ct.kilometrage) AS km_moyen,COUNT(DISTINCT ct.bus_id) AS nb_bus_entreprise
                           FROM controle_technique ct
                            JOIN bus b ON b.id_bus = ct.bus_id
                            JOIN entreprise e ON e.id_entreprise = b.entreprise_id
                           GROUP BY e.id_entreprise, e.nom_entreprise
                           ORDER BY nb_controles ASC
                           '''
    mycursor.execute(sql)
    stats_entreprise = mycursor.fetchall()

    return render_template('ctrl_technique/etat_ctrl_technique.html',stats_globales=stats_globales,stats_entreprise=stats_entreprise)


# ########################################### BUS ##########################################################

@app.route('/bus/show', methods=['GET'])
def show_bus():
    mycursor = get_db().cursor()
    sql = '''  SELECT b.id_bus AS id, 
               b.poids, 
               b.nb_passager, 
               b.date_achat, 
               b.entreprise_id,
               e.nom_entreprise AS nom,
               r.libelle_reservoir
        FROM bus b
        JOIN entreprise e ON b.entreprise_id = e.id_entreprise
        LEFT JOIN possede p ON b.id_bus = p.bus_id_possede
        LEFT JOIN reservoir r ON p.reservoir_id_possede = r.id_reservoir
        ORDER BY b.id_bus ASC
         '''
    mycursor.execute(sql)

    liste_bus = mycursor.fetchall()
    return render_template('bus/show_bus.html', bus=liste_bus)


@app.route('/bus/add', methods=['GET'])
def add_bus():
    print('''affichage du formulaire pour saisir un bus''')
    mycursor = get_db().cursor()
    sql = '''   SELECT id_entreprise AS id, nom_entreprise AS nom
                FROM entreprise
                    '''
    mycursor.execute(sql)
    type_entreprise = mycursor.fetchall()

    sql = '''   SELECT id_reservoir AS id, libelle_reservoir
                FROM reservoir'''
    mycursor.execute(sql)
    type_reservoir = mycursor.fetchall()


    return render_template('bus/add_bus.html', entreprise=type_entreprise, reservoir=type_reservoir)

@app.route('/bus/add',methods=['POST'])
def valid_add_bus():
    poids = request.form.get('poids', '')
    nb_passager = request.form.get('nb_passager', '')
    date_achat = request.form.get('date_achat', '')
    entreprise_id = request.form.get('entreprise_id', '')
    reservoir_id = request.form.get('reservoir_id', '')

    message = u'Bus ajouté, poids: ' + str(poids) + ' nb_passager: ' + str(nb_passager) + ' date_achat: ' + date_achat + ' entreprise: ' + entreprise_id + ' reservoir: ' + reservoir_id

    mycursor = get_db().cursor()

    tuple_param = (poids, nb_passager, date_achat, entreprise_id)
    sql = '''INSERT INTO bus(id_bus, poids, nb_passager, date_achat, entreprise_id)
             VALUES (NULL, %s, %s, %s, %s)'''

    mycursor.execute(sql, tuple_param)

    bus_id = mycursor.lastrowid
    from datetime import date
    date_installe = date.today()
    tuple_param_possede = (bus_id, reservoir_id, date_installe)
    sql_possede = '''INSERT INTO possede(bus_id_possede, reservoir_id_possede, date_installe)
                         VALUES (%s, %s, %s)'''
    mycursor.execute(sql_possede, tuple_param_possede)

    get_db().commit()
    flash(message, 'alert-success')
    return redirect('/bus/show')


@app.route('/bus/edit', methods=['GET'])
def edit_bus():
    print('''affichage du formulaire pour modifier un bus''')
    print(request.args.get('id'))
    id = request.args.get('id')
    mycursor = get_db().cursor()

    sql = '''SELECT b.id_bus,
                    b.poids,
                    b.nb_passager,
                    b.date_achat           AS dateAchat,
                    b.entreprise_id,
                    p.reservoir_id_possede AS reservoir_id
             FROM bus b
                      LEFT JOIN possede p ON b.id_bus = p.bus_id_possede
             WHERE b.id_bus = %s'''
    mycursor.execute(sql, (id,))
    bus = mycursor.fetchone()

    sql = '''SELECT id_entreprise AS id, nom_entreprise AS nom
             FROM entreprise'''
    mycursor.execute(sql)
    entreprises = mycursor.fetchall()

    sql = '''SELECT id_reservoir AS id, libelle_reservoir
             FROM reservoir'''
    mycursor.execute(sql)
    reservoirs = mycursor.fetchall()

    return render_template('bus/edit_bus.html', bus=bus, entreprise=entreprises, reservoir=reservoirs)


@app.route('/bus/edit', methods=['POST'])
def valid_edit_bus():
    print('''modification du bus''')
    id = request.form.get('id', '')
    poids = request.form.get('poids', '')
    nb_passager = request.form.get('nb_passager', '')
    date_achat = request.form.get('date_achat', '')
    entreprise_id = request.form.get('entreprise_id', '')
    reservoir_id = request.form.get('reservoir_id', '')

    message = u'Bus modifié, id: ' + id + ' poids: ' + str(poids) + ' nb_passager: ' + str(
        nb_passager) + ' date_achat: ' + date_achat + ' entreprise: ' + entreprise_id + ' reservoir: ' + reservoir_id
    print(message)

    mycursor = get_db().cursor()

    tuple_param = (poids, nb_passager, date_achat, entreprise_id, id)
    sql = '''UPDATE bus
             SET poids         = %s,
                 nb_passager   = %s,
                 date_achat    = %s,
                 entreprise_id = %s
             WHERE id_bus = %s'''
    mycursor.execute(sql, tuple_param)

    from datetime import date
    date_installe = date.today()

    sql_delete = '''DELETE FROM possede 
                   WHERE bus_id_possede = %s'''
    mycursor.execute(sql_delete, (id,))

    tuple_param_possede = (id, reservoir_id, date_installe)
    sql_possede = '''INSERT INTO possede(bus_id_possede, reservoir_id_possede, date_installe)
                     VALUES (%s, %s, %s)'''
    mycursor.execute(sql_possede, tuple_param_possede)

    get_db().commit()
    flash(message, 'alert-success')
    return redirect('/bus/show')



@app.route('/bus/delete', methods=['GET'])
def delete_bus():
    print('''suppression d'un bus''')
    print(request.args)
    print(request.args.get('id'))
    id = request.args.get('id')

    mycursor = get_db().cursor()

    sql = '''DELETE FROM consomme WHERE bus_id_consomme = %s'''
    mycursor.execute(sql, (id,))

    sql = '''DELETE FROM parcours WHERE bus_id_parcours = %s'''
    mycursor.execute(sql, (id,))

    sql = '''DELETE FROM se_ravitaille WHERE bus_id_ravitaille = %s'''
    mycursor.execute(sql, (id,))

    sql = '''DELETE FROM possede WHERE bus_id_possede = %s'''
    mycursor.execute(sql, (id,))

    sql = '''DELETE FROM controle_technique WHERE bus_id = %s'''
    mycursor.execute(sql, (id,))

    sql = '''DELETE FROM bus WHERE id_bus = %s'''
    mycursor.execute(sql, (id,))

    get_db().commit()

    message = u'un bus a été supprimé, id : ' + id
    print(message)
    flash(message, 'alert-warning')
    return redirect('/bus/show')


@app.route('/etat/bus', methods=['GET'])
def etat_bus():
    mycursor = get_db().cursor()

    sql = '''
        SELECT COUNT(DISTINCT b.id_bus) AS total_bus,
               AVG(b.poids) AS poids_moyen,
               AVG(b.nb_passager) AS capacite_moyenne,
               MAX(b.nb_passager) AS capacite_max,
               MIN(b.nb_passager) AS capacite_min,
               MAX(b.date_achat) AS achat_recent,
               MIN(b.date_achat) AS achat_ancien,
               COUNT(DISTINCT b.entreprise_id) AS nb_entreprises
        FROM bus b
    '''
    mycursor.execute(sql)
    stats_globales = mycursor.fetchone()

    sql = '''
        SELECT e.nom_entreprise,
               COUNT(b.id_bus) AS nb_bus,
               AVG(b.poids) AS poids_moyen,
               AVG(b.nb_passager) AS capacite_moyenne,
               SUM(b.nb_passager) AS capacite_totale
        FROM bus b
        JOIN entreprise e ON e.id_entreprise = b.entreprise_id
        GROUP BY e.id_entreprise, e.nom_entreprise
        ORDER BY nb_bus DESC
    '''
    mycursor.execute(sql)
    stats_entreprise = mycursor.fetchall()

    sql = '''
        SELECT r.libelle_reservoir,
               COUNT(DISTINCT p.bus_id_possede) AS nb_bus_equipes,
               AVG(b.poids) AS poids_moyen_bus
        FROM reservoir r
        LEFT JOIN possede p ON r.id_reservoir = p.reservoir_id_possede
        LEFT JOIN bus b ON b.id_bus = p.bus_id_possede
        GROUP BY r.id_reservoir, r.libelle_reservoir
        ORDER BY nb_bus_equipes DESC
    '''
    mycursor.execute(sql)
    stats_reservoir = mycursor.fetchall()

    return render_template('bus/etat_bus.html',
                          stats_globales=stats_globales,
                          stats_entreprise=stats_entreprise,
                          stats_reservoir=stats_reservoir)

########################################### PROBLÈME ##########################################################

@app.route('/probleme/show', methods=['GET'])
def show_probleme():
    mycursor = get_db().cursor()
    sql = '''  SELECT p.id_probleme AS id,
                      p.descriptif_probleme,
                      p.date_probleme AS date_probleme,
                      p.duree_maintenance,
                      c.libelle_categorie
        FROM probleme p
        JOIN categorie c ON c.id_categorie = p.categorie_id
        ORDER BY duree_maintenance
         '''
    mycursor.execute(sql)

    liste_control = mycursor.fetchall()
    return render_template('probleme/show_probleme.html', Probleme=liste_control)


@app.route('/probleme/add', methods=['GET'])
def add_probleme():
    print('''affichage du formulaire pour saisir un probleme''')
    mycursor = get_db().cursor()

    sql = '''SELECT id_categorie AS id, libelle_categorie
             FROM categorie'''
    mycursor.execute(sql)
    type_ctrl = mycursor.fetchall()

    sql = '''SELECT id_maintenance AS id, descriptif, date_revision
             FROM maintenance
             ORDER BY date_revision DESC'''
    mycursor.execute(sql)
    maintenances = mycursor.fetchall()

    return render_template('probleme/add_probleme.html', categorie=type_ctrl, maintenance=maintenances)

@app.route('/probleme/add',methods=['POST'])
def valid_add_probleme():
    descriptif_probleme = request.form.get('descriptif_probleme','')
    dateProbleme = request.form.get('dateProbleme','')
    duree_maintenance = request.form.get('duree_maintenance','')
    categorie_id = request.form.get('categorie_id','')
    maintenance_id = request.form.get('maintenance_id','')

    message = u'problème ajouté, descriptif_probleme: ' + descriptif_probleme + 'dateProbleme : ' + dateProbleme + ' categorie_id: ' + categorie_id + ' maintenance_id: ' + str(maintenance_id) + ' duree: ' + str(duree_maintenance)
    print(message)

    mycursor = get_db().cursor()
    tuple_param = (descriptif_probleme, dateProbleme, duree_maintenance, categorie_id, maintenance_id)
    sql = '''
          INSERT INTO probleme(id_probleme, descriptif_probleme, date_probleme, duree_maintenance, categorie_id, maintenance_id)
          VALUES (NULL, %s, %s, %s, %s, %s);
          '''
    print(sql, tuple_param)
    mycursor.execute(sql, tuple_param)
    get_db().commit()
    flash(message, 'alert-success')
    return redirect('/probleme/show')





@app.route('/probleme/edit', methods=['GET'])
def edit_probleme():
    print('''affichage du formulaire pour modifier un probleme''')
    print(request.args.get('id'))
    id = request.args.get('id')
    mycursor = get_db().cursor()
    sql = '''   SELECT p.id_probleme AS id, \
                        p.descriptif_probleme,\
                       p.date_probleme         AS dateProbleme, \
                        p.duree_maintenance,\
                       p.categorie_id     AS categorie, \
                       bus_id
                FROM probleme p
                WHERE p.id_probleme= %s;      '''
    mycursor.execute(sql, (id,))
    Probleme = mycursor.fetchone()

    sql = '''   SELECT id_bus AS id
                FROM bus '''
    mycursor.execute(sql)
    bus = mycursor.fetchall()

    return render_template('probleme/edit_probleme.html', Probleme=Probleme, bus=bus)


@app.route('/probleme/edit', methods=['POST'])
def valid_edit_probleme():
    print('''modification de la salle''')
    id = request.form.get('id', '')
    descriptif_probleme = request.form.get('descriptif_probleme', '')
    dateProbleme = request.form.get('dateProbleme', '')
    duree_maintenance = request.form.get('duree_maintenance', '')
    categorie_id = request.form.get('categorie_id', '')
    bus_id = request.form.get('bus_id', '')
    message = u'type ajouté , id: ' + id + 'descriptif_probleme:' + descriptif_probleme + ' dateProbleme: ' + dateProbleme + ' duree_maintenance: ' + duree_maintenance + 'categorie_id' + categorie_id + ' bus_id: ' + bus_id
    print(message)

    tuple_param = (descriptif_probleme, dateProbleme, duree_maintenance, categorie_id, bus_id)
    mycursor = get_db().cursor()
    sql = '''
          UPDATE probleme
          SET descriptif_probleme= %s, \
              date_probleme= %s, \
              duree_maintenance= %s,
              categorie_id= %s, \
              bus_id= %s
          WHERE id_probleme = %s;'''
    mycursor.execute(sql, tuple_param)

    get_db().commit()

    flash(message, 'alert-success')
    return redirect('/probleme/show')


@app.route('/probleme/delete', methods=['GET'])
def delete_probleme():
    print('''suppression d'un probleme''')
    print(request.args)
    print(request.args.get('id'))
    id = request.args.get('id')

    tuple_param = (id)
    mycursor = get_db().cursor()
    sql = '''DELETE \
             FROM probleme p \
             WHERE id_probleme = %s; \
          '''
    mycursor.execute(sql, tuple_param)

    get_db().commit()

    message = u'un probleme a été supprimé, id : ' + id
    print(message)
    flash(message, 'alert-warning')
    return redirect('/probleme/show')


@app.route('/etat/probleme', methods=['GET'])
def etat_probleme():
    mycursor = get_db().cursor()

    # stats global des controles techniques
    sql= '''
                         SELECT COUNT(DISTINCT ct.id_ctrl_technique) AS total_controles,
                                COUNT(DISTINCT ct.bus_id) AS nb_bus_controles,
                                AVG(ct.kilometrage) AS kilometrage_moyen,
                                MAX(ct.kilometrage) AS kilometrage_max,
                                MIN(ct.kilometrage) AS kilometrage_min,
                                MAX(ct.date_controle_technique) AS dernier_controle,
                                MIN(ct.date_controle_technique) AS premier_controle
                         FROM controle_technique ct
                         '''
    mycursor.execute(sql)
    stats_globales = mycursor.fetchone()

    # stats par entreprise
    sql = '''
                           SELECT e.nom_entreprise,COUNT(ct.id_ctrl_technique) AS nb_controles,AVG(ct.kilometrage) AS km_moyen,COUNT(DISTINCT ct.bus_id) AS nb_bus_entreprise
                           FROM controle_technique ct
                            JOIN bus b ON b.id_bus = ct.bus_id
                            JOIN entreprise e ON e.id_entreprise = b.entreprise_id
                           GROUP BY e.id_entreprise, e.nom_entreprise
                           ORDER BY nb_controles ASC
                           '''
    mycursor.execute(sql)
    stats_entreprise = mycursor.fetchall()

    return render_template('probleme/etat_probleme.html',stats_globales=stats_globales,stats_entreprise=stats_entreprise)



if __name__ == '__main__':
    app.run()
