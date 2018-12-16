import os, sqlite3
from ExсelConverter.table_descriptor import SQLTableDescriptor
from ExсelConverter.exel_parser import XLSXParser
from ExсelConverter.sql_enums import TypeEnum as TE
from ExсelConverter.SQLMaping import SQLiteMapClass, MySQLMapClass


class DBCreator:
    def __init__(self, file_path):
        super().__init__()
        self.parser = XLSXParser(file_path)
        exel_dis = self.parser.parse_headline()
        self.sheets = exel_dis['sheets']
        self.tables = {}
        for i, sheet in enumerate(self.sheets):  # создаем таблички
            self.tables[i] = SQLTableDescriptor(i, sheet, exel_dis['col'][sheet])

    def change_atr_index(self, table_index: int, old_index: int, new_index: int):
        if table_index in self.tables.keys():
            self.tables[table_index].change_atr_index(old_index, new_index)

    def change_atr_name(self,  table_index: int, atr_index: int, name: str):
        if table_index in self.tables.keys():
            self.tables[table_index].change_atr_name(atr_index, name)

    def change_atr_type(self,  table_index: int, atr_index: int, atr_type: str, varchar_num: int):
        if table_index in self.tables.keys():
            self.tables[table_index].change_atr_type(atr_index, atr_type, varchar_num)

    def change_atr_constraint(self, table_index: int, atr_index: int, constraint: str):
        if table_index in self.tables.keys():
            return self.tables[table_index].change_atr_constraint(atr_index, constraint)

    def change_atr_foreign_key(self, table_index: int, atr_index: int, fk_table: str, fk_atr: str):
        if table_index in self.tables.keys():
            self.tables[table_index].change_atr_foreign_key(atr_index, fk_table, fk_atr)

    def delete_atr(self, table_index: int, atr_index: int):
        if table_index in self.tables.keys():
            self.tables[table_index].delete_atr(atr_index)

    def get_insert_command(self, table: SQLTableDescriptor, row)->str:
        attributes_names = ''
        values = ''
        for key in table.attributes.keys():
            attributes_names += '\'' + table[key].name + '\', '
            if key < 0 or key >= len(row):
                return ''

            if table[key].atr_type == TE.int or table[key].atr_type == TE.real:
                values += row[key] + ', '
            else:
                values += '\'' + row[key] + '\', '

        command = 'INSERT INTO %s ( %s ) VALUES ( %s )' \
                  % (table.name, attributes_names[:-2], values[:-2])

        return command


    def create_SQLite_db(self, path: str, file_name:str)->[]:
        file_path = os.path.join(path, file_name + SQLiteMapClass.get_extension())
        conn = sqlite3.connect(file_path)
        cursor = conn.cursor()
        errors = []
        for key in self.tables.keys():
            command = self.tables[key].generate_command(SQLiteMapClass)
            try:
                cursor.execute(command)
            except Exception:
                errors.append('Ошибка при создании таблицы ' + self.tables[key].name)
                break

            data = self.parser.get_data_by_sheet_name(self.sheets[key])
            for i, row in enumerate(data):
                command = self.get_insert_command(self.tables[key], row)
                try:
                    cursor.execute(command)
                except Exception as ex:
                    errors.append('Ошибка при добавлении строки № %s в таблицу %s: %s'
                                  % (str(i), self.tables[key].name, ex))

        conn.commit()
        cursor.close()
        conn.close()
        return errors

    def create_SQLite_txt(self, path: str, file_name):
        file_path = os.path.join(path, file_name + '.txt')
        command = 'Скрипты сгенерированы с помощью ExcelConverter \n'
        for key in self.tables.keys():
            command += self.tables[key].generate_command(SQLiteMapClass) + '\n'

            data = self.parser.get_data_by_sheet_name(self.sheets[key])
            for i, row in enumerate(data):
                command += self.get_insert_command(self.tables[key], row) + '\n'

            command += '\n\n'

        with open(file_path, "tw", encoding='utf-8') as file:
            file.write(command)

    def create_MySQL_txt(self, path: str, file_name):
        file_path = os.path.join(path, file_name + '.txt')
        command = 'Скрипты сгенерированы с помощью ExcelConverter \n'
        for key in self.tables.keys():
            command += self.tables[key].generate_command(MySQLMapClass) + '\n'

            data = self.parser.get_data_by_sheet_name(self.sheets[key])
            for i, row in enumerate(data):
                command += self.get_insert_command(self.tables[key], row) + '\n'

            command += '\n\n'

        with open(file_path, "tw", encoding='utf-8') as file:
            file.write(command)
