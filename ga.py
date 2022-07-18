# from httplib2 import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import datetime
import calendar

# 環境変数読み込み
load_dotenv(".env")
SCOPES = [os.environ.get("SCOPES")]
KEY_FILE_LOCATION = os.environ.get("KEY_FILE_LOCATION")
VIEW_ID = os.environ.get("VIEW_ID")

# credentials = ServiceAccountCredentials.from_json_keyfile_name(
#     KEY_FILE_LOCATION, SCOPES)
# service = build("analytics", "v3", credentials=credentials)

# active_users = service.data().realtime().get(
#     ids="ga:" + VIEW_ID, metrics="rt:activeUsers").execute()
# pprint.pprint(active_users)

# 取得するレポートの範囲(日付)
# 2022年1月
year = 2022
month = 1
endDate = calendar.monthrange(year, month)[1]
report_startDate = datetime.date(year, month, 1)
report_endDate = datetime.date(year, month, endDate)


def initialize_analyticsreporting():
    """Initializes an Analytics Reporting API V4 service object.

    Returns:
      An authorized Analytics Reporting API V4 service object.
    """
    credentials = ServiceAccountCredentials.from_json_keyfile_name(
        KEY_FILE_LOCATION, SCOPES)

    # Build the service object.
    analytics = build('analyticsreporting', 'v4', credentials=credentials)

    return analytics


# レポートの取得(ここで何を取得するかの設定をする)
def get_report(analytics):
    """Queries the Analytics Reporting API V4.

    Args:
      analytics: An authorized Analytics Reporting API V4 service object.
    Returns:
      The Analytics Reporting API V4 response.
    """
    return analytics.reports().batchGet(
        body={
            'reportRequests': [
                {
                    'viewId': VIEW_ID,
                    # 'dateRanges': [{'startDate': '7daysAgo', 'endDate': 'today'}],
                    'dateRanges': [{'startDate': f"{report_startDate}", 'endDate': f"{report_endDate}"}],
                    'metrics': [{'expression': 'ga:sessions'}],
                    'dimensions': [{'name': 'ga:country'}]
                }]
        }
    ).execute()


def print_response(response):
    """Parses and prints the Analytics Reporting API V4 response.

    Args:
      response: An Analytics Reporting API V4 response.
    """
    for report in response.get('reports', []):
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get(
            'metricHeader', {}).get('metricHeaderEntries', [])

        for row in report.get('data', {}).get('rows', []):
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            # 日本からのセッション数のみ取得
            for header, dimension in zip(dimensionHeaders, dimensions):
                if dimension == "Japan":
                    print(header + ': ' + dimension)

            # セッション数表示 国ごと
            for i, values in enumerate(dateRangeValues):
                if dimension == "Japan":
                    print('Date range: ' + str(i))
                    for metricHeader, value in zip(metricHeaders, values.get('values')):
                        print(metricHeader.get('name') + ': ' + value)


def main():
    analytics = initialize_analyticsreporting()
    response = get_report(analytics)
    print_response(response)


if __name__ == '__main__':
    main()
