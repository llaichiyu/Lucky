import codecs
import os
import re
from time import sleep
from xml.etree import ElementTree

from flask import render_template

from app.utils.send_email import send_email


class Report:

    def __init__(self, project_id, build_no):
        self.project_id = project_id
        self.build_no = build_no

    def build_report(self):

        return render_template('report.html',
                               project_id=self.project_id,
                               build_no=self.build_no,
                               summary=self.__parser_summary())

    def send_email(self, app, category):
        output_dir = os.getcwd() + "/logs/%s/%s" % (self.project_id, self.build_no)
        output_dir = output_dir.replace("\\", "/")
        while not os.path.exists(output_dir + "/output.xml"):
            sleep(1)
        if category == 'http':
            sleep(10)
        elif category == 'web':
            sleep(30)
        else:
            sleep(100)

        res = self.__parser_summary()
        report_url = output_dir + "/report.html"
        log = codecs.open(output_dir + "/logs.log", "r", encoding="cp936").read().replace("\n", "<br>")
        send_email(app, res['name'], self.build_no, res['status'], res['starttime'], res['endtime'], report_url, log)

    def __parser_summary(self):
        summary = {}
        output_dir = os.getcwd() + "/logs/%s/%s" % (self.project_id, self.build_no)
        output_dir = output_dir.replace("\\", "/")
        tree = ElementTree.parse(output_dir + "/output.xml")
        root = tree.getroot()

        summary["generated"] = root.attrib["generated"]
        summary["generator"] = root.attrib["generator"]
        summary["name"] = root.find("./suite").attrib["name"]
        summary["build_no"] = self.build_no
        summary["starttime"] = root.find("./suite/status").attrib["starttime"]
        summary["endtime"] = root.find("./suite/status").attrib["endtime"]
        summary["status"] = root.find("./suite/status").attrib["status"]
        summary["pass"] = root.find("./statistics/suite/stat").attrib["pass"]
        summary["fail"] = root.find("./statistics/suite/stat").attrib["fail"]
        return summary

    def parser_detail_info(self):
        detail_data = []
        output_dir = os.getcwd() + "/logs/%s/%s" % (self.project_id, self.build_no)
        output_dir = output_dir.replace("\\", "/")
        tree = ElementTree.parse(output_dir + "/output.xml")
        root = tree.getroot()
        for test in root.iter("test"):
            detail_data.append({
                "status": test.find("status").attrib["status"].lower(),
                "name": test.attrib["name"].split(" ")[1],
                "starttime": test.find("status").attrib["starttime"],
                "endtime": test.find("status").attrib["endtime"]
            })
            for kw in test.iter("kw"):
                text = ""
                image = ""
                for msg in kw.iter("msg"):
                    if "<a" in msg.text:
                        img = re.findall('src="images/(.+)" width', msg.text)
                        if len(img) != 0:
                            image = img[0]
                    else:
                        text = text + msg.text + "<br>"
                """    
                msg = kw.find("msg")
                if msg is not None:
                    text = kw.find("msg").text

                if "<a" in text:
                    image = re.findall('src="images/(.+)" width', text)[0]
                """
                detail_data.append({
                    "status": kw.find("status").attrib["status"].lower(),
                    "keyword": kw.attrib["name"],
                    "msg": text,
                    "image": image,
                    "project_id": self.project_id,
                    "build_no": self.build_no
                })
                print(text)

        return detail_data