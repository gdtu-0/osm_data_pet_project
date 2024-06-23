from dataclasses import dataclass # type: ignore
from typing import Optional, List, Dict, Tuple

# Import Dagster
from dagster import DagsterLogManager

# Import resource definition
from ...resources.pg_target_db import Target_PG_DB

@dataclass
class Table:
    """Database table"""

    # WHERE condition is passed as list of dicts
    # Each dict must have column name as key and conditional value as value
    # Only '=' comparator is supported
    # Elements within dict are combined with AND condition
    # Dicts in list are combined with OR condition

    name: str   # Database table name
    column_specs: Dict  # Dict structure of table fields where key is a field name
                        # and value is column definition
    _db_resource: Optional[Target_PG_DB] = None  # Database resource
    
    def __post_init__(self) -> None:
        """Post init hook"""

        self.exists = False     # Table exists in database
        self.columns = tuple(self.column_specs.keys())  # List of table column names
    
    def __dict_to_where_cond(self, dict: Dict) -> str:
        """Convert dict to where condition"""

        return "( " + " AND ".join(f"{col_name} = \'{value}\'" for col_name, value in dict.items()) + " )"
    
    def __generate_where_str(self, where: List[Dict]) -> str:
        """Helper function to generate WHERE condition string"""

        return "WHERE\n  " + " OR\n  ".join(self.__dict_to_where_cond(elem) for elem in where)

    
    def link_to_resource(self, resource: Target_PG_DB) -> None:
        """Get DB resource and check if table exists"""
        
        self._db_resource = resource
        self.exists = self._db_resource.table_exists(self.name)
    

    def create(self, log: Optional[DagsterLogManager] = None) -> None:
        """Create table in database"""

        columns_str = ",\n  ".join(f'{name} {specs}' for name, specs in self.column_specs.items())
        create_str = f"CREATE TABLE {self.name} (\n  {columns_str}\n)"
        sql_str = f"{create_str};"
        self._db_resource.exec_sql_no_fetch(sql = sql_str)
        if log:
            log.info(f"SQL statement:\n\n{sql_str}")

    
    def select(self, columns: Optional[Tuple] = None, where: Optional[List[Dict]] = None, log: Optional[DagsterLogManager] = None) -> List[Dict]:
        """Select statement"""

        if columns:
            columns_str = ", ".join(name for name in columns)
        else:
            columns_str = ", ".join(name for name in self.columns)
        select_str = f"SELECT\n  {columns_str}\n"
        from_str = f"FROM {self.name}"
        if where:
            where_str = "\n" + self.__generate_where_str(where)     # For how to build where condition read description above
        else:
            where_str = ''
        sql_str = f"{select_str}{from_str}{where_str};"
        result = self._db_resource.exec_sql_dict_cursor(sql = sql_str)
        if log:
            if result:
                log.info(f"SQL statement:\n\n{sql_str}\n\nResults:\n\n  " + ",\n  ".join(str(row) for row in result))
            else:
                log.info(f"SQL statement:\n\n{sql_str}\n\nResults:\n\n  {result}")  # In case of None
        if result:
            return result
        else:
            return []
    

    def delete(self, where: List[Dict], log: Optional[DagsterLogManager] = None) -> None:
        """Delete statement"""

        delete_str = f"DELETE FROM {self.name}\n"
        where_str = self.__generate_where_str(where)     # For how to build where condition read description above
        sql_str = f"{delete_str}{where_str};"
        self._db_resource.exec_sql_no_fetch(sql = sql_str)
        if log:
            log.info(f"SQL statement:\n\n{sql_str}")
    

    def insert(self, values: List[Tuple], log: Optional[DagsterLogManager] = None) -> None:
        """Insert statement"""

        columns_str = ", ".join(name for name in self.columns)
        insert_str = f"INSERT INTO {self.name}\n  ({columns_str})\nVALUES %s"
        sql_str = f"{insert_str}"
        self._db_resource.exec_insert(sql = sql_str, values = values)
        if log:
            log.info(f"SQL statement:\n\n{sql_str}\n  " + ",\n  ".join(str(elem) for elem in values))