#!/usr/bin/env python
"""
This is the "example" module.

The example module supplies one function, factorial().  For example,

>>> escape('"hello""')
'\"\"hello\"\"\"\"'
>>> save(parser.parse_args(["save", "-db", "test.db", "-table","snippt", "-name","测试key", "-value","测试value"]))
>>> get(parser.parse_args(["get", "-db", "test.db", "-table","snippt", "-name","测试key"]))
'测试value'
>>> listall(parser.parse_args(["list", "-db", "test.db", "-table","snippt"]))
'(测试key, 测试value)'
>>> listall(parser.parse_args(["list", "-action", "name", "-db", "test.db", "-table","snippt"]))
'测试key'
>>> import os; os.remove("test.db")
"""
import argparse
import re
import sqlite3
from typing import Any


parser = argparse.ArgumentParser(description="使用sqlite的本地存储")
subparsers = parser.add_subparsers(help="子命令 help")

savecommand = subparsers.add_parser("save", help="保存值")
savecommand.set_defaults(func=lambda i: save(i))
savecommand.add_argument("-db", dest="db", required=True, type=str)
savecommand.add_argument("-table", dest="table", required=True, type=str)
savecommand.add_argument("-name", dest="name", required=True, type=str)
savecommand.add_argument("-value", dest="value", required=True, type=str)

getcommand = subparsers.add_parser("get", help="获取值")
getcommand.set_defaults(func=lambda i: get(i))
getcommand.add_argument("-db", dest="db", required=True, type=str)
getcommand.add_argument("-table", dest="table", required=True, type=str)
getcommand.add_argument("-name", dest="name", required=True, type=str)

listcommand = subparsers.add_parser("list", help="获取所有值")
listcommand.set_defaults(func=lambda i: listall(i))
listcommand.add_argument(
    "-action", dest="action", choices=["name", "all"], default="all", type=str
)
listcommand.add_argument("-db", dest="db", required=True, type=str)
listcommand.add_argument("-table", dest="table", required=True, type=str)


def escape(words: str) -> str:
    return re.sub('"', '""', words)


def save(args: argparse.Namespace) -> None:
    """保存信息"""
    conn = sqlite3.connect(args.db)

    try:
        c = conn.cursor()
        c.execute(
            (
                """CREATE TABLE IF NOT EXISTS {} (
            id     INTEGER PRIMARY KEY,
            key           CHAR(100)    NOT NULL UNIQUE,
            value           TEXT     NOT NULL);"""
            ).format(args.table)
        )
        c.execute(
            (
                """
            INSERT OR REPLACE INTO {} (key, value) values ("{}", "{}")
            """
            ).format(args.table, escape(args.name), escape(args.value))
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass
    finally:
        conn.close()


def get(args: argparse.Namespace) -> str:
    """
    读取信息

    """
    conn = sqlite3.connect(args.db)
    conn.text_factory = str

    try:
        c = conn.cursor()
        cursor = c.execute(
            'SELECT value from {} where key = "{}"'.format(args.table, args.name)
        )
        res = []
        for row in cursor:
            res.append(row[0])
        return ",".join(res)
    except sqlite3.OperationalError:
        return "读取失败"
    finally:
        conn.close()


def listall(args: argparse.Namespace) -> str:
    """
    返回所有值
    """
    conn = sqlite3.connect(args.db)
    conn.text_factory = str
    c = conn.cursor()

    try:
        if args.action == "all":
            cursor = c.execute("SELECT key, value from {}".format(args.table))
            return ",".join("({}, {})".format(row[0], row[1]) for row in cursor)
        else:
            cursor = c.execute("SELECT key from {}".format(args.table))
            return ",".join(tuple(row[0] for row in cursor))
    except sqlite3.OperationalError:
        return ""
    finally:
        conn.close()


if __name__ == "__main__":
    args = parser.parse_args()
    print(args.func(args))
