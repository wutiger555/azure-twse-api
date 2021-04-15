import logging
import azure.functions as func
import requests
import datetime
import json
import time
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup as bs


def request(period):
    # parameter init
    now = datetime.datetime.today()
    if (period == 'biannual'):
        SDATE = str((now - relativedelta(months=6)).strftime("%Y%m%d"))  # 起始日期
    elif (period == 'weekly'):
        SDATE = str((now - relativedelta(weeks=1)).strftime("%Y%m%d"))  # 起始日期
    else:
        return func.HttpResponse(
                    "req params: period not existed.",
                    mimetype="application/json",
                    status_code=204
                )

    EDATE = str(now.strftime("%Y%m%d"))  # 結束日期
    YEAR1 = str(now.year-1911)  # 起始年
    YEAR2 = YEAR1  # 結束年
    MONTH1 = str(now.month)  # 起始月
    MONTH2 = YEAR1  # 年？
    SDAY = str(now.day)  # 起始日
    EDAY = (now - relativedelta(months=1)).strftime("%d")  # 結束日
    scope = '2'
    sort = '2'
    rpt = "bool_t67sb07"
    firstin = '1'
    step = '2'
    typek = "pub"
    encodeURIComponent = '1'
    data = "encodeURIComponent="+encodeURIComponent+"&typek="+typek+"&step="+step+"&firstin="+firstin + \
        "&rpt="+rpt+"&sort="+sort+"&scope="+scope+"&EDAY="+EDAY+"&SDAY="+SDAY+"&MONTH2="+MONTH2+"&MONTH1="+MONTH1 + \
        "&YEAR1="+YEAR1+"&YEAR2="+YEAR2+"&EDATE="+EDATE+"&SDATE="+SDATE
    data_month = "encodeURIComponent=1&step=2&typek=pub&co_id_1=&SDATE=20200925&EDATE=20210325&YEAR1=109&YEAR2=110&MONTH1=9&MONTH2=110&SDAY=25&EDAY=25&scope=2&sort=1&rpt=bool_t67sb07&firstin=1"
    url = "https://mops.twse.com.tw/mops/web/ajax_t146sb10"

    logging.info("Python HTTP trigger function processed a request.")
    for i in range(0, 10):
        try:
            r = requests.post(url, data=data)
        except:
            if(i == 10):
                logging.exception("Request Failed with url:",
                                  url, "\n data:", data)
                return func.HttpResponse(
                    "Requests POST Failed.\n Please contact the developer.",
                    mimetype="application/json",
                    status_code=408
                )
            time.sleep(3)
            continue
    logging.info("start parsing html file to json.")
    soup = bs(r.text, 'html.parser')
    form = soup.find("form")
    trs = form.find_all("tr")
    list = []
    # 一則公告 ['公司代號', '公司簡稱', '公告日期', '主　　旨','詳細資料']
    for tr in trs:
        tds = tr.find_all("td")
        # 確認是否有指定關鍵字在公告中
        hasTitle = False
        # 一則公告中的一行
        temp = []
        dict = {}
        for td in tds:
            if ("不動產" in td.text or "土地" in td.text or "建照" in td.text or "工程" in td.text) and \
                "基金" not in td.text and "信託" not in td.text and  \
                    "續租" not in td.text and "解除契約" not in td.text and "終止" not in td.text:
                hasTitle = True
            if td.find("input"):
                # 詳細資料拼網址
                if hasTitle:
                    _attr = td.find("input").attrs["onclick"].replace("document.fm_t67sb07.", "") \
                        .replace("openWindow(this.form ,\"\");", "").replace(".value", "").replace("\"", "")
                    attr = _attr.split(";")
                    parameter = attr[0]+"&"+attr[1]+"&"+attr[2]+"&"+attr[3]
                    temp.append("https://mops.twse.com.tw/mops/web/t146sb10" +
                                attr[4].replace("action=", "")+"?"+parameter+"&TYPEK=pub&firstin=1")
                    temp.append(parameter+"&TYPEK=pub&firstin=1")

            else:
                temp.append(td.text)
        if hasTitle:
            dict['公司代號'] = temp[0]
            dict['公司簡稱'] = temp[1]
            dict['公告日期'] = temp[2]
            dict['主旨'] = temp[3]
            dict['詳細資料'] = temp[4]
            logging.info(dict)
            list.append(dict)
    # field names
    json_string = json.dumps(list)
    return json_string


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HTTP trigger function processed a request.')
    period = req.params.get('period')

    r = request(period)
    # jsonResponse = parseRequest(r)
    if r:
        return func.HttpResponse(
            r,
            mimetype="application/json",
            status_code=200
        )
    else:
        return func.HttpResponse(
            "Request Failed.\n Please contact the developer.",
            mimetype="application/json",
            status_code=404
        )
