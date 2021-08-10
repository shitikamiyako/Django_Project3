from os import path
import sqlite3

import click
import pandas

SQL_POS = "../db.sqlite3"


@click.command()
@click.argument("source_file", type=click.Path(exists=True))
@click.argument("destination_db", default=SQL_POS, type=click.Path(exists=True))
@click.argument("destination_table_name", type=str)
@click.option("-r", "--DROP-DB", default=False, confirmation_prompt=True, help="DROP TABLE BEFORE INJECT.", is_flag=True)
@click.option("-d", "--dry-run", default=False, help="make it dry-run mode.", is_flag=True)
def inject(source_file, destination_db, destination_table_name, drop_db, dry_run):
    """Inject data from datafile."""
    if dry_run:
        print(source_file)
        print(destination_db)
        print(dry_run)
        print(drop_db)
        return None

    source_data: pandas.DataFrame = read_data(source_file)
    with sqlite3.connect(destination_db) as sqlite_con:

        # Enable Foreign key support.  <https://www.sqlitetutorial.net/sqlite-foreign-key/>
        sqlite_con.execute(
            """PRAGMA foreign_keys = ON;""")

        if not check_existence_table_name(destination_table_name, sqlite_con):
            NameError("SQL table you specified is not found.")

        if drop_db:  # if drop_db is set, then trancate all data from the dest table.
            delete_state = f"DELETE FROM {destination_table_name}"
            sqlite_con.execute(delete_state)
            sqlite_con.commit()

        source_data.to_sql(destination_table_name, sqlite_con,
                           if_exists="append", index=False)


def check_existence_table_name(table_name, con):
    """Check existence of table name."""
    table_list = [i[0] for i in con.execute(
        "select name from sqlite_master where type='table'").fetchall()]
    return table_name in table_list


def read_data(source):
    """read data for json/csv."""
    extention = path.splitext(source)

    if extention[1] == ".json":  # splitext will have dot + extension.
        return pandas.read_json(source)
    elif extention[1] == ".csv":
        return pandas.read_csv(source)
    else:
        NotImplementedError("This util only accepts csv/json formated files.")


def create_option(flag_mode) -> dict:
    """Create pandas.to_sql option from flag."""
    if flag_mode:
        return {"if_exists": "replace"}
    else:
        return {"if_exists": "append"}


if __name__ == "__main__":
    inject()
