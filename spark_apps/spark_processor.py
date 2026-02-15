from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, first, last, max, min
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType, ArrayType, TimestampType

spark = SparkSession.builder.appName("StockPulseAnalytics").getOrCreate()

schema = StructType([
    StructField("data", ArrayType(StructType([
        StructField("p", DoubleType()),
        StructField("s", StringType()),
        StructField("t", LongType()),
        StructField("v", DoubleType())
    ]))),
    StructField("type", StringType())
])

raw_df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9093") \
    .option("subscribe", "raw_ticks") \
    .option("startingOffsets", "earliest") \
    .load()

parsed_df = raw_df.select(from_json(col("value").cast("string"), schema).alias("json")) \
    .selectExpr("explode(json.data) as trade") \
    .select(
        col("trade.s").alias("symbol"),
        col("trade.p").alias("price"),
        (col("trade.t") / 1000).cast(TimestampType()).alias("timestamp")
    )

ohlc_df = parsed_df \
    .withWatermark("timestamp", "1 minute") \
    .groupBy(window(col("timestamp"), "1 minute"), col("symbol")) \
    .agg(
        first("price").alias("open"),
        max("price").alias("high"),
        min("price").alias("low"),
        last("price").alias("close")
    )

# query = ohlc_df.writeStream \
#     .outputMode("update") \
#     .format("console") \
#     .option("truncate", "false") \
#     .start()

query = ohlc_df.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("path", "/data/ohlc_output") \
    .option("checkpointLocation", "/tmp/checkpoint") \
    .start()

query.awaitTermination()