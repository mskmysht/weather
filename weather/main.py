import sys
import textwrap
import pandas as pd
from datetime import date
import argparse

def read_weather_stats(prec_no: str, block_no: int, year: int, month: int) -> pd.DataFrame:
    df = pd.read_html(
        f"https://www.data.jma.go.jp/obd/stats/etrn/view/daily_s1.php?prec_no={prec_no}&block_no={block_no}&year={year}&month={month}&day=&view=p1"
        )[0][['日', '気温(℃)', '湿度(％)']]
    df.columns = ['day', 'avg_temp', 'max_temp', 'low_temp', 'avg_hum', 'low_hum']
    df.insert(0, 'month', month)
    df.insert(0, 'year', year)
    return df.dropna()

def get_prec_data(prec_code: str, wmo_id: int, date_from: date, date_to: date):
    assert date_from < date_to

    dfs = []
    if date_from.year == date_to.year:
        year = date_from.year
        if date_from.month == date_to.month:
            month = date_from.month
            dfs.append(
                read_weather_stats(prec_code, wmo_id, year, month) \
                    .query(f'{date_from.day} <= day <= {date_to.day}')
            )
        else:
            dfs.append(
                read_weather_stats(prec_code, wmo_id, year, date_from.month) \
                    .query(f'day >= {date_from.day}')
            )
            for m in range(date_from.month + 1, date_to.month):
                dfs.append(
                    read_weather_stats(prec_code, wmo_id, year, m)
                )
            dfs.append(
                read_weather_stats(prec_code, wmo_id, year, date_to.month) \
                    .query(f'day <= {date_to.day}')
            )
    else:
        dfs.append(
            read_weather_stats(prec_code, wmo_id, date_from.year, date_from.month) \
                .query(f'day >= {date_from.day}')
        )

        for m in range(date_from.month + 1, 13):
            dfs.append(
                read_weather_stats(prec_code, wmo_id, date_from.year, m)
            )
    
        for y in range(date_from.year + 1, date_to.year):
            for m in range(1, 13):
                dfs.append(
                    read_weather_stats(prec_code, wmo_id, y, m)
                )
    
        for m in range(1, date_to.month):
            dfs.append(
                read_weather_stats(prec_code, wmo_id, date_to.year, m)
            )

        dfs.append(
            read_weather_stats(prec_code, wmo_id, date_to.year, date_to.month) \
                .query(f'day <= {date_to.day}')
        )

    return pd.concat(dfs)

class MyHelpFormatter(argparse.RawTextHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass

def main():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(
            """
            過去の気象データを取得する。
            データは以下のヘッダを持つCSV形式で標準出力される。
             - year: 観測年
             - month: 観測月
             - day: 観測日
             - avg_temp: 一日の平均気温
             - max_temp: 一日の最高気温
             - low_temp: 一日の最低気温
             - avg_hum: 一日の平均湿度
             - low_hum: 一日の最低湿度
            """
        ).strip(),
        formatter_class=MyHelpFormatter)
    parser.add_argument('prec_no', type=str, help='都道府県コード')
    parser.add_argument(
        'wmo_id', type=int,
        help=textwrap.dedent(
            """
            世界気象機関(WMO)が定める数字５桁の識別子
            識別子の一覧は https://oscar.wmo.int/oscar/vola/vola_legacy_report.txt の`IndexNbr`列を参照。
            定義の詳細は http://www.weathergraphics.com/identifiers/ を参照。
            """
            ).strip()
        )
    parser.add_argument('date_from', type=str, help='取得データの開始日（YYYY-MM-DD）')
    parser.add_argument('date_to', type=str, help='取得データの終了日（YYYY-MM-DD）')
    args = parser.parse_args()

    df = get_prec_data(args.prec_no, args.wmo_id,
                       date.fromisoformat(args.date_from), date.fromisoformat(args.date_to)) 

    df.to_csv(sys.stdout, index=False)
