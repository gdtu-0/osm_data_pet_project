from dataclasses import dataclass # type: ignore
from typing import Optional, List, Dict, Tuple

# Import Dagster
from dagster import DagsterLogManager

# Import resource definition
from ...resources.pg_target_db import Target_PG_DB

@dataclass
class Table:
    """Database table"""

    name: str   # Database table name
    column_specs: Dict  # Dict structure of table fields where key is a field name
                        # and value is column definition
    _db_resource: Optional[Target_PG_DB] = None  # Database resource
    
    def __post_init__(self) -> None:
        """Post init hook"""

        self.exists = False     # Table exists in database
        self.columns = tuple(self.column_specs.keys())  # List of table column names
    
    def link_to_resource(self, resource: Target_PG_DB) -> None:
        """Get DB resource and check if table exists"""
        
        self._db_resource = resource
        self.exists = self._db_resource.table_exists(self.name)
    

    def create(self, log: Optional[DagsterLogManager] = None, logging_enabled: bool = False) -> None:
        """Create table in database"""

        columns_str = ",\n  ".join(f'{name} {specs}' for name, specs in self.column_specs.items())
        create_str = f"CREATE TABLE {self.name} (\n  {columns_str}\n)"
        sql_str = f"{create_str};"
        self._db_resource.exec_sql_no_fetch(sql = sql_str)
        if log and logging_enabled:
            log.info(f"SQL statement:\n\n{sql_str}")

    
    def select(self, columns: Optional[Tuple] = None, where: Optional[Dict] = None, log: Optional[DagsterLogManager] = None, logging_enabled: bool = False) -> Optional[List[Dict]]:
        """Select statement"""

        # Very basic functionality
        # For WHERE condition only EQ operator is implemented
        # Different columns in WHERE combined with AND
        # Does not support duplicate columns in WHERE 
        # Values in WHERE are quoted, so numeric types are not supported
    
        if columns:
            columns_str = ", ".join(name for name in columns)
        else:
            columns_str = ", ".join(name for name in self.columns)
        select_str = f"SELECT\n  {columns_str}\n"
        from_str = f"FROM {self.name}"
        if where:
            where_str = "\nWHERE\n  " + " AND\n  ".join(f"{col_name} = \'{val}\'" for col_name, val in where.items())
        else:
            where_str = ''
        sql_str = f"{select_str}{from_str}{where_str};"
        result = self._db_resource.exec_sql_dict_cursor(sql = sql_str)
        if log and logging_enabled:
            if result:
                log.info(f"SQL statement:\n\n{sql_str}\n\nResults:\n\n  " + ",\n  ".join(str(row) for row in result))
            else:
                log.info(f"SQL statement:\n\n{sql_str}\n\nResults:\n\n  {result}")  # In case of None
        return result
    

    def delete(self, where: Dict, log: Optional[DagsterLogManager] = None, logging_enabled: bool = False) -> None:
        """Delete statement"""

        delete_str = f"DELETE FROM {self.name}\n"
        where_str = "WHERE\n  " + " AND\n  ".join(f"{col_name} = \'{val}\'" for col_name, val in where.items())
        sql_str = f"{delete_str}{where_str};"
        self._db_resource.exec_sql_no_fetch(sql = sql_str)
        if log and logging_enabled:
            log.info(f"SQL statement:\n\n{sql_str}")
    

    def insert(self, values: List[Tuple], log: Optional[DagsterLogManager] = None, logging_enabled: bool = False) -> None:
        """Insert statement"""

        columns_str = ", ".join(name for name in self.columns)
        insert_str = f"INSERT INTO {self.name}\n  ({columns_str})\nVALUES %s"
        sql_str = f"{insert_str}"
        self._db_resource.exec_insert(sql = sql_str, values = values)
        if log and logging_enabled:
            log.info(f"SQL statement:\n\n{sql_str}\n  " + ",\n  ".join(str(elem) for elem in values))