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

def write_to_postgres(batch_df, batch_id):
    # Flatten the window struct so it matches our table columns
    db_df = batch_df.select(
        col("symbol"),
        col("window.start").alias("window_start"),
        col("window.end").alias("window_end"),
        col("open").alias("open_price"),
        col("high").alias("high_price"),
        col("low").alias("low_price"),
        col("close").alias("close_price")
    )

    # Use the JDBC driver to sink data
    # Note: Using 'append' mode here with the DB primary key handles updates
    db_df.write \
        .format("jdbc") \
        .option("url", "jdbc:postgresql://postgres_db:5432/stock_analytics") \
        .option("dbtable", "ohlc_candles") \
        .option("user", "stockpulse") \
        .option("password", "password123") \
        .option("driver", "org.postgresql.Driver") \
        .mode("append") \
        .save()

query = ohlc_df.writeStream \
    .outputMode("update") \
    .foreachBatch(write_to_postgres) \
    .option("checkpointLocation", "/opt/bitnami/spark/spark_apps/checkpoints") \
    .start()

query.awaitTermination()