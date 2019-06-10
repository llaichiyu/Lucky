#!/usr/bin/env python
# -*- coding:utf-8 -*-
#@Time  : 2019/6/10 9:50
#@user: xws
#@File  : user_keyword.py

from datetime import datetime
from flask_restful import Resource, reqparse
from flask_login import current_user
from sqlalchemy import and_

from app.ext import db
from app.models import User, UserKeywordSuite, UserKeyword


class UserKeywordSuiteApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int, default=-1)
        self.parser.add_argument('project_id', type=int)
        self.parser.add_argument('category', type=str)
        self.parser.add_argument('name', type=str)
        self.parser.add_argument('desc', type=str)
        self.parser.add_argument('tags', type=str)
        self.parser.add_argument('prev', type=int)
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('enable', type=bool, default=True)
        self.parser.add_argument('setup', type=str)
        self.parser.add_argument('teardown', type=str)
        self.parser.add_argument('page', type=int, default=1)
        self.parser.add_argument('rows', type=int, default=15)

    def get(self):
        args = self.parser.parse_args()

        pagination = UserKeywordSuite.query.filter_by(project_id=args["project_id"]).order_by(UserKeywordSuite.id.asc()).paginate(
            args["page"], per_page=args["rows"],
            error_out=False
        )

        suites = pagination.items
        data = {"total": pagination.total, "rows": []}
        for s in suites:
            data["rows"].append({
                "id": s.id,
                "project_id": s.project_id,
                "name": s.name,
                "desc": s.desc,
                "create_user": User.query.filter_by(id=s.create_user_id).first().username,
                "create_timestamp": s.create_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                "update_user": User.query.filter_by(id=s.update_user_id).first().username,
                "update_timestamp": s.update_timestamp.strftime("%Y-%m-%d %H:%M:%S")
            })

        return data

    def post(self):
        args = self.parser.parse_args()

        method = args["method"].lower()
        if method == "create":
            return self.__create(args), 201
        elif method == "edit":
            return self.__edit(args), 201
        elif method == "delete":
            return self.__delete(args), 201

        return {"status": "fail", "msg": "方法: %s 不支持" % method}, 201

    def __create(self, args):
        result = {"status": "success", "project_id": args["project_id"],
                  "msg": "操作成功"}

        suite = UserKeywordSuite.query.filter(and_(UserKeywordSuite.name == args["name"],
                                                       UserKeywordSuite.project_id == args["project_id"])).first()
        if suite is None:
            try:
                suite = UserKeywordSuite(name=args["name"],
                                             desc=args["desc"],
                                             project_id=args["project_id"],
                                             tags=args["tags"],
                                             category=args["category"],
                                             enable=args["enable"],
                                             setup=args["setup"],
                                             teardown=args["teardown"],
                                             create_user_id=current_user.get_id(),
                                             update_user_id=current_user.get_id())

                db.session.add(suite)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "异常：%s" % str(e)
        else:
            result["status"] = "fail"
            result["msg"] = "用户关键字集名称[%s]重复" % args["name"]

        return result


    def __edit(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}
        suite = UserKeywordSuite.query.filter_by(id=args["id"]).first()
        if suite is None:
            result["status"] = "fail"
            result["msg"] = "未找到要修改的用户关键字集id"
        else:
            try:
                suite.name = args["name"]
                suite.desc = args["desc"]
                suite.tags = args["tags"]
                suite.enable = args["enable"]
                suite.setup = args["setup"]
                suite.teardown = args["teardown"]

                suite.update_user_id = current_user.get_id()
                suite.update_timestamp = datetime.now()

                db.session.merge(suite)
                db.session.commit()

                result["project_id"] = suite.project_id

            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "编辑用户关键字集[id-%s]失败：%s" % (args["id"], str(e))

        return result

    def __delete(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}

        suite = UserKeywordSuite.query.filter_by(id=args["id"]).first()
        if suite is None:
            result["status"] = "fail"
            result["msg"] = "未找到要删除的用户关键字集id"
        else:
            try:
                result["project_id"] = suite.project_id
                db.session.delete(suite)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "删除用户关键字集[id-%s]失败：%s" % (args["id"], str(e))

        return result


class UserKeywordApi(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id', type=int, default=-1)
        self.parser.add_argument('method', type=str)
        self.parser.add_argument('suite_id', type=int)
        self.parser.add_argument('keyword', type=str)
        self.parser.add_argument('params', type=str)
        self.parser.add_argument('prev', type=int)

    def get(self):
        args = self.parser.parse_args()
        data = {"total": 10, "rows": []}
        if args["id"] != -1:

            k = UserKeyword.query.filter_by(id=args["id"]).first()
            data["rows"] = eval(k.params)
        else:
            for i in range(1, 11):
                data["rows"].append({
                    "param_0": i,
                    "param_1": "",
                    "param_2": "",
                    "param_3": "",
                    "param_4": ""
                })

        return data


    def post(self):
        args = self.parser.parse_args()

        method = args["method"].lower()
        if method == "create":
            return self.__create(args), 201
        elif method == "edit":
            return self.__edit(args), 201
        elif method == "delete":
            return self.__delete(args), 201

        return {"status": "fail", "msg": "方法: %s 不支持" % method}, 201

    def __create(self, args):
        result = {"status": "success",
                  "msg": "创建关键字[%s]成功" % args["keyword"]}

        suite = UserKeyword.query.filter(and_(UserKeyword.keyword == args["keyword"],
                                                  UserKeyword.keyword_suite_id == args["suite_id"])).first()
        if suite is None:
            try:
                keyword = UserKeyword(keyword=args["keyword"],
                                          params=args["params"],
                                          keyword_suite_id=args["suite_id"],
                                          create_user_id=current_user.get_id(),
                                          update_user_id=current_user.get_id())

                db.session.add(keyword)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "异常：%s" % str(e)
        else:
            result["status"] = "fail"
            result["msg"] = "用户关键字[%s]重复" % args["keyword"]

        return result

    def __edit(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}
        keyword = UserKeyword.query.filter_by(id=args["id"]).first()
        if keyword is None:
            result["status"] = "fail"
            result["msg"] = "未找到要修改的用户关键字id"
        else:
            try:
                keyword.keyword = args["keyword"]
                keyword.params = args["params"]
                keyword.keyword_suite_id = args["suite_id"]
                keyword.update_user_id = current_user.get_id()
                keyword.update_timestamp = datetime.now()

                db.session.merge(keyword)
                db.session.commit()

                result["suite_id"] = keyword.keyword_suite_id

            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "编辑用户关键字[id-%s]失败：%s" % (args["id"], str(e))

        return result

    def __delete(self, args):
        result = {"status": "success",
                  "msg": "操作成功"}

        keyword = UserKeyword.query.filter_by(id=args["id"]).first()
        if keyword is None:
            result["status"] = "fail"
            result["msg"] = "未找到要删除的用户关键字id"
        else:
            try:
                db.session.delete(keyword)
                db.session.commit()
            except Exception as e:
                result["status"] = "fail"
                result["msg"] = "删除用户关键字[id-%s]失败：%s" % (args["id"], str(e))

        return result
