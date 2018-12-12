from typing import List, Dict


class TableDescriptor:
    def __init__(self):
        pass


class Attribute:
    def __init__(self, index: int, name: str):
        self.index = index
        self.name = name
        self.atr_type = ''
        self.constraints = []
        self.fk_table = ''
        self.fk_atr = ''
        self.ALLOWED_CONSTRAINTS = []
        self.ALLOWED_TYPES = []


class SQLiteAttribute(Attribute):
    def __init__(self, index: int, name: str, atr_type: str,):
        super().__init__(index, name)
        self.ALLOWED_CONSTRAINTS = ['PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE', 'AUTOINCREMENT', 'NOT NULL']
        self.ALLOWED_TYPES = ['INTEGER', 'REAL', 'TEXT']

        if atr_type.strip() in self.ALLOWED_TYPES:
            self.atr_type = atr_type.strip()

    def change_constraint(self, constraint: str):
        if constraint.strip() in self.constraints:  # del
            self.constraints.remove(constraint.strip())
        elif constraint.strip() in self.ALLOWED_CONSTRAINTS:  # add
            self.constraints.append(constraint.strip())

    def change_foreign_key(self, foreign_key_table: str, foreign_key_atr: str):
        if foreign_key_table is None:
            pass
        elif foreign_key_table.strip() == '':
            self.fk_table = ''
        else:
            self.fk_table = foreign_key_table

        if foreign_key_atr is None:
            pass
        elif foreign_key_atr.strip() == '':
            self.fk_atr = ''
        else:
            self.fk_atr = foreign_key_atr

    def change_name(self, name: str):
        self.name = name.strip()

    def change_type(self, atr_type: str):
        if atr_type.strip() in self.ALLOWED_TYPES:
            self.atr_type = atr_type.strip()


class SQLiteTableDescriptor(TableDescriptor):

    def __init__(self, table_index, table_name, attributes: List[str]):
        super().__init__()
        self.index = table_index
        self.name = table_name

        self.attributes = {}
        for i, atr in enumerate(attributes):
            self.attributes[i] = (SQLiteAttribute(i, atr, 'TEXT'))

    def change_atr_index(self, old_index: int, new_index: int):
        if old_index in self.attributes.keys() and new_index not in self.attributes.keys():
            self.attributes[new_index] = self.attributes.pop(old_index)
            self.attributes[new_index].index = new_index

    def __getitem__(self, item):
        if item in self.attributes.keys():
            return self.attributes[item]

    def change_atr_name(self, index: int, name: str):
        if index in self.attributes.keys():
            self.attributes[index].change_name(name)

    def change_atr_type(self, index: int, atr_type: str):
        if index in self.attributes.keys():
            self.attributes[index].change_type(atr_type)

    def change_atr_constraint(self, index: int, constraint: str):
        if index in self.attributes.keys():
            self.attributes[index].change_constraint(constraint)

    def change_atr_foreign_key(self, index: int, fk_table: str, fk_atr: str):
        if index in self.attributes.keys():
            self.attributes[index].change_foreign_key(fk_table, fk_atr)

    def delete_atr(self, index: int):
        if index in self.attributes.keys():
            self.attributes.pop(index, None)

    def generate_command(self)->str:
        command = ''
        primary_key = ''
        auto_inc = False
        for i in self.attributes.keys():
            atr = self.attributes[i]
            command += ",\n \'" + atr.name + "\'"  # add attribute
            command += ' ' + atr.atr_type        # with type
            for con in atr.constraints:          # and constraints
                if con == 'AUTOINCREMENT':
                    command += ' PRIMARY KEY AUTOINCREMENT'
                    auto_inc = True
                elif con == 'PRIMARY KEY' and not auto_inc:
                    primary_key += "'" + atr.name + "',\n "  # создаем primary key
                else:
                    command += ' ' + con

            if atr.fk_table is not None and atr.fk_atr is not None:  # add foreign_key
                if atr.fk_table != '' and atr.fk_atr != '':
                    command += ',\n FOREIGN KEY ( %s ) REFERENCES %s(%s) ON DELETE CASCADE ON UPDATE NO ACTION'\
                           % (atr.name, atr.fk_table, atr.atr.fk_atr)

        command = command[3:]

        if not primary_key == '' and not auto_inc:
            command += ', PRIMARY KEY ( %s )' % (primary_key[:-3])

        command = "CREATE TABLE '%s' \n ( %s )" % (self.name, command)

        return command
