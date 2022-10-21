#!/usr/bin/python
# -*- coding: utf-8 -*-

import sqlite3
from sqlite3 import Error
import os.path

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# If modifying these scopes, delete the file token.json.
SPREAD_SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = '1AuRlFWDJb8M0kyDNAN6qf2P8h9_RPzGSgMyR1J0WQuY'
CREDENTIALS_TOKE_FILE = 'token.json'
WORK_SHEET_NAME_MENU = 'menu'
WORK_SHEET_NAME_STEP = 'step'
WORK_SHEET_NAME_INGREDIENT = 'ingredient'
WORK_SHEET_NAME_MENU_INGREDIENT = 'menu_ingredient'
WORK_SHEET_NAME_MENU_TYPE = 'menu_type'



def get_wks(wks_id, wks_name):
    cred = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_TOKE_FILE, SPREAD_SCOPES)
    gc = gspread.authorize(cred)
    print("try to connect " + wks_name)
    wks = gc.open_by_key(wks_id).worksheet(wks_name)
    print("wks success " + wks.title)
    return wks


def generate_db_with_wks_connection(db_file,
                                    create_db_command,
                                    insert_db_command,
                                    insert_db_param):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("connect file: " + db_file)
        cur = conn.cursor()
        # print("create_db_command: {}".format(create_db_command))
        cur.execute(create_db_command)
        # print("insert_db_command: {}".format(insert_db_command))
        # print("insert_db_param: {}".format(insert_db_param))
        cur.executemany(insert_db_command, insert_db_param)
        conn.commit()
    except Exception as e:
        print("db error: ", e)
    finally:
        if conn:
            conn.close()


def get_create_db_command(db_name, db_param):
    db_create_command = ""
    for i in range(0, len(db_param)):
        if i != 0:
            db_create_command += ','
        db_create_command += str(db_param[i])
    return '''CREATE TABLE {} ({})'''.format(db_name, db_create_command)


def get_insert_db_command(db_name, param_size):
    db_insert_command = ""
    for i in range(0, param_size):
        if i != 0:
            db_insert_command += ','
        db_insert_command += '?'
    return '''INSERT INTO {} VALUES ({})'''.format(db_name, db_insert_command)


def get_insert_db_param(worksheet_value, db_name,
                        row_range, col_range, col_except):
    insert_param = []
    for row_id in range(row_range[0], row_range[1]):
        try:
            row_value = worksheet_value[row_id]
            # print("[{}] row {}: value: {}".format(db_name, row_id, row_value))
            invalid_data = False
            insert_col_val = []
            for col_id in range(col_range[0], col_range[1]):
                col_value = row_value[col_id]
                if col_id in col_except:
                    continue
                if str(col_value) == '':
                    invalid_data = True
                    break
                insert_col_val.append(col_value)
        except Exception as ex:
            invalid_data = True
            print("[{}] find exception error at row {}, error: {}".format(db_name, row_id, ex))

        if invalid_data:
            print("[{}] find invalid data at row {}".format(db_name, row_id))
            break

        print("[{}] row {}: value: {}".format(db_name, row_id, insert_col_val))
        insert_param.append(tuple(insert_col_val))
    return insert_param  # insert_command


def query_db(db_file, db_name):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print("connect file: " + db_file)
        cur = conn.cursor()
        cur.execute('''SELECT * from {}'''.format(db_name))
        results = cur.fetchall()
        print("find results size: " + str(len(results)))
        for r in results:
            print("result:" + str(r))

    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def generate_db(db_name, dest_assets_db_path,
                db_param, param_size,
                work_sheet_name,
                row_range, col_range,
                col_except=[]
                ):
    try:
        os.remove(dest_assets_db_path)
    except FileNotFoundError:
        print("[{}] {} not found".format(db_name, dest_assets_db_path))

    db_file_name = '{}.db'.format(db_name)
    try:
        os.remove(db_file_name)
    except FileNotFoundError:
        print("[{}] {} not found".format(db_name, db_file_name))

    wks = get_wks(SPREADSHEET_ID, work_sheet_name)

    # check if out of range
    print("[{}] row_count: {},  col_count: {}".format(db_name, wks.row_count, wks.col_count))
    row_range[1] = row_range[1] if row_range[1] < wks.row_count else wks.row_count
    col_range[1] = col_range[1] if col_range[1] < wks.col_count else wks.col_count

    generate_db_with_wks_connection(
        r"{}".format(db_file_name),
        get_create_db_command(db_name, db_param),
        get_insert_db_command(db_name, param_size),
        get_insert_db_param(
            wks.get_all_values(),
            # db_name
            db_name,
            # row start / end
            row_range,
            # column start / end
            col_range,
            # col_except
            col_except
        )
    )

    query_db('{}'.format(db_file_name), db_name)
    os.rename(db_file_name, dest_assets_db_path)


if __name__ == '__main__':

    # menu db
    generate_db('menu_db', '../assets/menu_db/menu.db',
                # db_param
                ('id INTEGER PRIMARY KEY', 'name VARCHAR', 'description TEXT',
                 'image TEXT', 'size INTEGER', 'source INTEGER', 'vegetarian INTEGER',
                 'video_link TEXT', 'cook_time INTEGER'),
                # param_size
                9,
                WORK_SHEET_NAME_MENU,
                # row start / end
                [2, 1000],
                # column start / end
                [0, 9]
                )

    # step db
    generate_db('step_db', '../assets/step_db/step.db',
                # db_param
                ('menu_id INTEGER', 'step_order INTEGER', 'description TEXT', 'PRIMARY KEY (menu_id, step_order)'),
                # param_size
                3,
                WORK_SHEET_NAME_STEP,
                # row start / end
                [2, 1000],
                # column start / end
                [0, 3]
                )

    # ingredient db
    generate_db('ingredient_db', '../assets/ingredient_db/ingredient.db',
                # db_param
                ('id INTEGER PRIMARY KEY', 'name VARCHAR', 'd_unit VARCHAR', 'unit INTEGER', 'image TEXT', 'type_id INTEGER', 'kcal INTEGER'),
                # param_size
                7,
                WORK_SHEET_NAME_INGREDIENT,
                # row start / end
                [2, 1000],
                # column start / end
                [0, 9],
                # col_except
                [2,4]
                )

    # menu ingredient db
    generate_db('menu_ingredient_db', '../assets/menu_ingredient_db/menu_ingredient.db',
                # db_param
                ('menu_id INTEGER', 'ingredient_id INTEGER', 'd_size FLOAT', 'size FLOAT',
                 'PRIMARY KEY (menu_id, ingredient_id)'),
                # param_size
                4,
                WORK_SHEET_NAME_MENU_INGREDIENT,
                # row start / end
                [2, 1000],
                # column start / end
                [0, 4]
                )

    generate_db('menu_type_db','../assets/menu_type_db/menu_type.db',
                #db_param
                ('menu_id INTEGER','type_id INTEGER',
                'PRIMARY KEY (menu_id, type_id)'),
                # param_size
                2,
                WORK_SHEET_NAME_MENU_TYPE,
                # row start/end
                [2,1000],
                # column start/end
                [0,2]
                )