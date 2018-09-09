class LiveData:

    def __str__(self) -> str:
        return self.id

    def __init__(self, id, pm2_5_1h, no2_1h, o3_1h, so2_1h, level, primary_pollutant, pm10_1h, city_name, city_pinyin,
                 action, affect, o3_8h, data_unit, aqi, time_point, co_1h):
        self.id = id
        self.pm2_5_1h = pm2_5_1h
        self.no2_1h = no2_1h
        self.o3_1h = o3_1h
        self.so2_1h = so2_1h
        self.level = level
        self.primary_pollutant = primary_pollutant
        self.pm10_1h = pm10_1h
        self.city_name = city_name
        self.city_pinyin = city_pinyin
        self.action = action
        self.affect = affect
        self.o3_8h = o3_8h
        self.data_unit = data_unit
        self.aqi = aqi
        self.time_point = time_point
        self.co_1h = co_1h


