print("Début du traitement de données NBA avec PySpark dans main.py")

try:
    import traceback
    from hdfs import InsecureClient
    from pyspark.sql import SparkSession, Window
    from pyspark.sql.functions import col, sum as spark_sum, lag
    import duckdb
    import os

    # Connexion HDFS
    hdfs_host = 'http://namenode:9870'
    hdfs_user = 'root'
    client = InsecureClient(hdfs_host, user=hdfs_user)

    # Chemins HDFS
    input_path = '/data_raw/api_nba/career_stats_ALL_20250828_232802.csv'
    output_path = '/data_processed/career_stats_clean.csv'

    # Colonnes à garder
    cols = [
        "PLAYER_ID","SEASON_ID","TEAM_ID","GP","MIN","FGM","FGA","FG_PCT",
        "FTM","FTA","FT_PCT","OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS"
    ]
    kpi_vars = ["GP","MIN","FGM","FGA","FG_PCT","FTM","FTA","FT_PCT",
                "OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS"]

    print("Initialisation SparkSession...")
    spark = SparkSession.builder.appName("NBAStatsProcessing").getOrCreate()

    print("Lecture du CSV depuis HDFS avec Spark...")
    df = spark.read.csv(f"hdfs://namenode:9000{input_path}", header=True, inferSchema=True)

    print("Suppression des doublons et sélection des colonnes...")
    df = df.dropDuplicates(["PLAYER_ID", "SEASON_ID"]).select(cols)

    print("Calcul des variations et pourcentages avec Spark...")
    window = Window.partitionBy("PLAYER_ID").orderBy("SEASON_ID")
    # Calcul des variations pour chaque KPI
    for kpi in kpi_vars:
        df = df.withColumn(f"{kpi}_VAR", col(kpi) - lag(col(kpi), 1).over(window))
        df = df.withColumn(f"{kpi}_PREV", lag(col(kpi), 1).over(window))

    # Calcule la somme des variations et la somme des valeurs précédentes pour chaque ligne
    var_cols = [f"{kpi}_VAR" for kpi in kpi_vars]
    prev_cols = [f"{kpi}_PREV" for kpi in kpi_vars]
    df = df.withColumn("TOTAL_KPI_VAR", spark_sum(col(c) for c in var_cols))
    df = df.withColumn("TOTAL_KPI_PREV", spark_sum(col(c) for c in prev_cols))
    df = df.withColumn("TOTAL_KPI_VAR_PCT", col("TOTAL_KPI_VAR") / col("TOTAL_KPI_PREV"))

    # Sélection finale des colonnes
    df = df.select(cols + ["TOTAL_KPI_VAR", "TOTAL_KPI_VAR_PCT"])

    print("Sauvegarde du résultat dans HDFS...")
    # Sauvegarde au format CSV dans HDFS
    df.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"hdfs://namenode:9000{output_path}")

    print("Lecture du fichier traité depuis HDFS pour DuckDB...")
    # Télécharge le fichier traité depuis HDFS pour DuckDB
    local_csv = "/tmp/career_stats_clean.csv"
    files = client.list('/data_processed')
    for f in files:
        if f.startswith('career_stats_clean.csv'):
            client.download(f"/data_processed/{f}", local_csv, overwrite=True)
            break

    print("Transfert dans DuckDB...")
    os.makedirs('./data/processed', exist_ok=True)
    duckdb_path = './data/processed/nba_stats.duckdb'
    con = duckdb.connect(duckdb_path)
    con.execute(f"CREATE TABLE IF NOT EXISTS career_stats AS SELECT * FROM read_csv_auto('{local_csv}')")
    con.close()

    print(f"Fichier transféré dans la base DuckDB : {duckdb_path}")

except Exception as e:
    print("Erreur lors du traitement :", e)
    traceback.print_exc()
    # Lit le fichier traité depuis HDFS
    with client.read(output_path, encoding='utf-8') as reader:
        df_processed = pd.read_csv(reader)

    # Sauvegarde dans DuckDB
    duckdb_path = './data/processed/nba_stats.duckdb'
    con = duckdb.connect(duckdb_path)
    con.execute("CREATE TABLE IF NOT EXISTS career_stats AS SELECT * FROM df_processed")
    con.close()

    print(f"Fichier transféré dans la base DuckDB : {duckdb_path}")

except Exception as e:
    print("Erreur lors du traitement :", e)
    traceback.print_exc()
