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
    print('''affichage du formulaire pour saisir une salle''')
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


if __name__ == '__main__':
    app.run()
