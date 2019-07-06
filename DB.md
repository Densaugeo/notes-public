# DB Notes

## MariaDB

~~~
SHOW DATABASES;
SHOW TABLES IN [Database];
CONNECT [Database];
SHOW TABLES;
CREATE TABLE [Table name] ([Column 1 name] [Type], [Column 2 name] [Type], ..., PRIMARY KEY ([Column name], [Another column name], ...));
SELECT * FROM [Table];
INSERT INTO [Table] VALUES ([Value 1], [Value 2], ...);
INSERT INTO [Table] VALUES ([Value 1], [Value 2], ...), ([Value 1], [Value 2], ...), ...;
~~~

## SQLite3

~~~
sqlite3 [database file]
.tables // Same as SHOW TABLES;
~~~
