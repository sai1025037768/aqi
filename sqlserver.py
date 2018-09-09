# -*- coding:utf-8 -*-
import pymssql


class MSSQL:
    def __init__(self, host, port, user, pwd, db):
        self.host = host
        self.port = port
        self.user = user
        self.pwd = pwd
        self.db = db

    def __GetConnect(self):
        if not self.db:
            raise (NameError, "没有设置数据库信息")
        self.conn = pymssql.connect(server=self.host, port=self.port, user=self.user, password=self.pwd,
                                    database=self.db,
                                    charset="UTF-8")
        cur = self.conn.cursor()
        if not cur:
            raise (NameError, "连接数据库失败")
        else:
            return cur

    def ExecQuery(self, sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        resList = cur.fetchall()

        # 查询完毕后必须关闭连接
        cur.close()
        self.conn.close()
        return resList

    def ExecNonQuery(self, sql):
        cur = self.__GetConnect()
        cur.execute(sql)
        self.conn.commit()
        self.conn.close()

    # INSERT
    # INTO
    # AQI.dbo.tbl_live_data
    # (id, pm2_5_1h, no2_1h, o3_1h, so2_1h, [level], primary_pollutant, pm10_1h, city_name, city_pinyin, [action], affect,
    #  o3_8h, data_unit, aqi, time_point, co_1h)
    # VALUES('', (NULL), (NULL), (NULL), (NULL), (NULL), (NULL), (NULL), (NULL), (NULL), (NULL), (NULL), (NULL), (NULL),
    #        (NULL), (NULL), (NULL));

    def execute_many(self, datas):
        cur = self.__GetConnect()
        try:
            sql = 'INSERT INTO tbl_live_data VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

            params = []
            for data in datas:
                param = (data.id, data.pm2_5_1h, data.no2_1h, data.o3_1h, data.so2_1h, data.level, data.primary_pollutant,
                         data.pm10_1h, data.city_name, data.city_pinyin, data.action, data.affect, data.o3_8h, data.data_unit,
                         data.aqi, data.time_point, data.co_1h)
                params.append(param)

            print(params)

            cur.executemany(sql, params)
            self.conn.commit()
        finally:
            # 插入完毕后必须关闭连接
            cur.close()
            self.conn.close()
