import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql import Window

def main():
    # Создаем spark-сессию
    spark = SparkSession.builder.master("local[*]").appName("crimes_in_boston").getOrCreate()

    # Произведем загрузку данных файла - offense_codes.csv
    df_codes_src = spark.read.format("csv").option("mode", "FAILFAST").option("inferSchema", "true") \
        .option("header", "true").option("encoding", "latin1").option("path", sys.argv[1]) \
        .load()

    # Формирование финального набора данных df_codes
    #   - Оставляем уникальные коды, взяв любое из названий в дубликатах.
    #   - Формируем столбец crime_type - первая часть NAME из таблицы offense_codes, разбитого по разделителю “-”
    #     (например, если NAME “BURGLARY - COMMERICAL - ATTEMPT”, то crime_type “BURGLARY”)
    df_codes = df_codes_src \
        .withColumn("row_num", row_number().over(Window.partitionBy("CODE").orderBy(col("NAME").desc()))) \
        .filter(col("row_num") == 1).drop("row_num") \
        .withColumn('CRIME_TYPE', substring_index("NAME", " -", 1)) \
        .orderBy(col("CODE"))

    # Произведем загрузку данных файла - crime.csv
    df_crime_src = spark.read.format("csv").option("mode", "FAILFAST").option("inferSchema", "true") \
        .option("header", "true").option("path", sys.argv[2]).option("encoding", "latin1") \
        .load()

    # Формирование финального набора данных df_crime
    # Сразу оставляем только необходимые столбцы из датасета
    # 1765 строк с пустыми значениями поля DISTRICT. Заменим такие значения на N/A и проведем расчет витрины
    df_crime = df_crime_src.select("DISTRICT", "YEAR", "MONTH", "OFFENSE_CODE", "Lat", "Long") \
        .withColumn('DISTRICT', when(df_crime_src.DISTRICT.isNull() , 'N/A') \
        .otherwise(df_crime_src.DISTRICT)) 

    # Объединяем набор данных df_crime с df_codes
    # df_crime = df_crime.join(broadcast(df_codes), df_crime['OFFENSE_CODE'] == df_codes['CODE']) \
    df_crime = df_crime.join(df_codes, df_crime['OFFENSE_CODE'] == df_codes['CODE']) \
        .drop("CODE", "NAME") \
        .cache()

    # Формируем промежуточные наборы данных для расчета витрины

    # Набор данных df_crimes_stat
    #   - crimes_total - Общее количество преступлений в этом районе
    df_crimes_stat = df_crime.groupBy(col("DISTRICT")) \
        .agg(count("*").alias("crimes_total")) \
        .orderBy(col("DISTRICT")) \
        .cache()

    # Набор данных df_crimes_lat_lng
    #   - lat - Широта координаты района, рассчитанная как среднее по всем широтам инцидентов
    #   - lng - Долгота координаты района, рассчитанная как среднее по всем долготам инцидентов
    # 20744 Строки с нулевыми или неверными значениями координат (-1) - при расчете средних значений 
    # широты и долготы инцидентов, такие строки отфильтруем
    df_crimes_lat_lng = df_crime.where("(Lat<>-1 AND Long<>-1) AND Lat IS NOT NULL AND Long IS NOT NULL") \
        .groupBy(col("DISTRICT")) \
        .agg(avg(col("Lat")).alias("lat"), avg(col("Long")).alias("lng")) \
        .withColumnRenamed("DISTRICT","DISTRICT_ID") \
        .orderBy(col("DISTRICT")) \
        .cache()

    # Набор данных df_crimes_monthly
    #   - crimes_monthly - медиана числа преступлений в месяц в этом районе
    # Реализуем через SQL Expression с функцией percentile_approx. 
    # Выполнение происходит в два раза быстрее - чем через SQL запрос с применением Temporary View 
    df_crimes_monthly = df_crime.groupBy("DISTRICT", "YEAR", "MONTH") \
        .agg(count("*").alias("month_crimes")) \
        .groupBy("DISTRICT") \
        .agg(expr('percentile_approx(month_crimes, 0.5)').alias("crimes_monthly")) \
        .withColumnRenamed("DISTRICT", "DISTRICT_ID") \
        .orderBy("DISTRICT_ID") \
        .cache()

    # Набор данных df_frequent_crime_types
    #   - frequent_crime_types - три самых частых crime_type за всю историю наблюдений в этом районе, 
    #     объединенных через запятую с одним пробелом ", " , расположенных в порядке убывания частоты
    df_frequent_crime_types = df_crime.groupBy("DISTRICT", "CRIME_TYPE") \
        .agg(count("*").alias("crimes_by_crime_type")) \
        .withColumn("row_num", row_number().over(Window.partitionBy("DISTRICT").orderBy(col("crimes_by_crime_type").desc()))) \
        .filter(col("row_num") <= 3).drop("row_num", "crimes_by_crime_type") \
        .groupBy("DISTRICT") \
        .agg(concat_ws(", ", collect_list(col("CRIME_TYPE"))).alias("frequent_crime_types")) \
        .withColumnRenamed("DISTRICT", "DISTRICT_ID") \
        .orderBy("DISTRICT_ID") \
        .cache()

    # Готовим ИТОГОВЫЙ НАБОР ДАННЫХ df_result
    #   - district - район 
    #   - crimes_total - общее количество преступлений в этом районе
    #   - crimes_monthly - медиана числа преступлений в месяц в этом районе
    #   - frequent_crime_types - три самых частых crime_type за всю историю наблюдений в этом районе, 
    #     объединенных через запятую с одним пробелом “, ” , расположенных в порядке убывания частоты
    #   - lat - широта координаты района, рассчитанная как среднее по всем широтам инцидентов
    #   - lng - долгота координаты района, рассчитанная как среднее по всем долготам инцидентов
    df_result = df_crimes_stat.join(df_crimes_monthly, df_crimes_stat['DISTRICT'] == df_crimes_monthly['DISTRICT_ID']) \
        .drop("DISTRICT_ID") \
        .join(df_frequent_crime_types, df_crimes_stat['DISTRICT'] == df_frequent_crime_types['DISTRICT_ID']) \
        .drop("DISTRICT_ID") \
        .join(df_crimes_lat_lng, df_crimes_stat['DISTRICT'] == df_crimes_lat_lng['DISTRICT_ID']) \
        .drop("DISTRICT_ID") \
        .select("DISTRICT", "crimes_total", "crimes_monthly", "frequent_crime_types", "lat", "lng") \
        .orderBy(col("DISTRICT"))

    # Сохраняем итоговый набор данных df_result в файл формата parquet
    df_result.coalesce(1).write.mode('overwrite').parquet(sys.argv[3])

    # Останавливаем spark-сессию
    spark.stop()

if __name__ == "__main__":
    # Проверяем аргументы вызова программы
    if len(sys.argv) != 4:
        print("Usage: Crimes_in_Boston [path to offense_codes.csv] [path to crime.csv] [path to output_folder]",
              file=sys.stderr)
        sys.exit(-1)

    main()
