#!/usr/bin/env python3
"""
But: produire UN SEUL fichier CSV directement sous /data_processed pour chaque résultat.
Stratégie:
 - Essayer d'écrire depuis le driver : df.toPandas() -> client.write(target)
 - Si trop volumineux ou erreur de mémoire, fallback :
    * écrire coalesce(1) dans un dossier tmp (Spark)
    * repérer part-*.csv
    * déplacer/renommer en target via "hdfs dfs -mv"
    * si mv indisponible ou échoue, downloader le part-file et re-uploader via InsecureClient

Ajout spécifique: pour la "question 1" (career_stats), calculer deux colonnes:
 - performance_variation : somme des variations absolues par rapport à la saison précédente
 - performance_variation_pct : pourcentage de cette variation par rapport à la somme des valeurs de la saison précédente
"""
import os
import time
import traceback
import subprocess
import tempfile
from functools import reduce

from hdfs import InsecureClient
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lag, abs as spark_abs, coalesce, lit, when
from pyspark.sql import Window
import duckdb  # Ajout de l'import

# Config HDFS
HDFS_RPC = "hdfs://namenode:9000"
HDFS_WEB = "http://namenode:9870"   # webhdfs
HDFS_USER = "root"
client = InsecureClient(HDFS_WEB, user=HDFS_USER)

# Paths
career_input = "/data_raw/api_nba/career_stats_ALL_20250828_232802.csv"
career_input_rpc = f"{HDFS_RPC}{career_input}"
career_target = "/data_processed/career_stats_clean.csv"
career_tmp = "/data_processed/_tmp_career_stats"

games_input_rpc = f"{HDFS_RPC}/data_raw/kaggle/game.csv"
spectacular_target = "/data_processed/spectacular_games.csv"
spectacular_tmp = "/data_processed/_tmp_spectacular_games"

# Safety threshold: if DF rows > COLLECT_THRESHOLD, skip to tmp fallback.
COLLECT_THRESHOLD = 50000  # adjust as needed

def run_cmd(cmd):
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        return (0, out.strip())
    except subprocess.CalledProcessError as e:
        return (e.returncode, e.output)

def hdfs_path_exists(path):
    try:
        return client.status(path, strict=False) is not None
    except Exception:
        return False

def hdfs_remove(path):
    return run_cmd(["hdfs", "dfs", "-rm", "-f", path])

def hdfs_rmdir(path):
    return run_cmd(["hdfs", "dfs", "-rm", "-r", "-skipTrash", path])

def find_part_file_in_tmp(tmp_dir):
    rc, out = run_cmd(["hdfs", "dfs", "-ls", tmp_dir])
    if rc != 0:
        return None, out
    for line in out.splitlines():
        parts = line.split()
        if len(parts) >= 8:
            path = parts[-1]
            if "/part-" in path or os.path.basename(path).startswith("part-"):
                return path, out
    return None, out

def move_part_to_target(part_path, target_path, tmp_dir):
    rc, out = run_cmd(["hdfs", "dfs", "-rm", "-f", target_path])
    rc, out_mv = run_cmd(["hdfs", "dfs", "-mv", part_path, target_path])
    if rc == 0:
        hdfs_rmdir(tmp_dir)
        return True, out_mv
    try:
        local_tmp = tempfile.mktemp(prefix="partfile_")
        client.download(part_path, local_tmp, overwrite=True)
        client.upload(target_path, local_tmp, overwrite=True)
        try:
            os.remove(local_tmp)
        except Exception:
            pass
        hdfs_rmdir(tmp_dir)
        return True, "moved via webhdfs download/upload"
    except Exception as e:
        return False, f"mv failed: {out_mv}\nfallback failed: {e}"

def write_text_to_hdfs_via_client(target_path, text):
    client.write(target_path, data=text, encoding='utf-8', overwrite=True)

def hdfs_head(path, n=10):
    # Correction : utiliser le chemin HDFS complet si non déjà présent
    if not path.startswith("hdfs://"):
        path = f"{HDFS_RPC}{path}"
    rc, out = run_cmd(["hdfs", "dfs", "-cat", path])
    if rc != 0:
        return out
    lines = out.splitlines()
    return "\n".join(lines[:n])

def add_performance_variation_columns(df, id_col="PLAYER_ID", season_col="SEASON_ID", stat_cols=None):
    """
    Ajoute deux colonnes au DataFrame df:
      - performance_variation : somme des variations absolues par rapport à la saison précédente
      - performance_variation_pct : pourcentage de variation par rapport à la somme des valeurs de la saison précédente

    df: DataFrame (contenant id_col, season_col et colonnes numériques dans stat_cols)
    stat_cols: liste des colonnes numériques à utiliser pour le calcul (si None on prend une liste par défaut intersect)
    """
    # colonnes attendues par défaut (comme dans ton pipeline)
    default_stats = [
        "GP","MIN","FGM","FGA","FG_PCT",
        "FTM","FTA","FT_PCT","OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS"
    ]
    if stat_cols is None:
        stat_cols = default_stats
    # garder seulement les colonnes réellement présentes
    stat_cols = [c for c in stat_cols if c in df.columns]
    if not stat_cols:
        # rien à faire
        return df

    # Window pour ordonner par saison par joueur
    w = Window.partitionBy(id_col).orderBy(season_col)

    # créer colonnes prev_<stat> = lag(stat)
    for c in stat_cols:
        df = df.withColumn(f"prev_{c}", lag(col(c)).over(w))

    # calculer somme des différences absolues et somme des valeurs précédentes
    abs_diff_exprs = [spark_abs(col(c) - col(f"prev_{c}")) for c in stat_cols]
    prev_sum_exprs = [coalesce(col(f"prev_{c}"), lit(0)) for c in stat_cols]

    total_abs = reduce(lambda a, b: a + b, abs_diff_exprs)
    prev_total = reduce(lambda a, b: a + b, prev_sum_exprs)

    # ajouter colonnes
    df = df.withColumn("performance_variation", total_abs.cast("double"))
    df = df.withColumn("performance_variation_pct",
                       when(prev_total == 0, lit(0.0)).otherwise((total_abs / prev_total * 100).cast("double")))

    # pour les premières saisons (prev all null), total_abs sera la somme d'abs(col - null) = null -> coalesce to 0
    # mais nos expressions produisent null si prev is null, on force 0 pour la première saison
    df = df.withColumn("performance_variation", coalesce(col("performance_variation"), lit(0.0)))
    df = df.withColumn("performance_variation_pct", coalesce(col("performance_variation_pct"), lit(0.0)))

    # supprimer colonnes temporaires prev_*
    prev_cols = [f"prev_{c}" for c in stat_cols]
    df = df.drop(*prev_cols)

    return df

def save_df_to_duckdb(df, local_duckdb_path, table_name="data"):
    """
    Enregistre un DataFrame Spark en DuckDB localement.
    """
    pdf = df.toPandas()
    con = duckdb.connect(local_duckdb_path)
    con.execute(f"CREATE TABLE {table_name} AS SELECT * FROM pdf")
    con.close()

def process_and_write(df, name, target_path, tmp_dir, spark):
    print(f"--- Processing {name} -> {target_path} ---")
    try:
        count = df.count()
        print(f"{name}: row count = {count}")
    except Exception as e:
        print(f"Erreur count() pour {name}: {e}")
        count = None

    # Try driver-based write if small enough
    if count is not None and count <= COLLECT_THRESHOLD:
        try:
            print(f"Attempting to collect {name} to driver (toPandas)...")
            pdf = df.toPandas()
            csv_text = pdf.to_csv(index=False)
            print(f"Writing {name} to HDFS via webhdfs (InsecureClient)...")
            write_text_to_hdfs_via_client(target_path, csv_text)
            time.sleep(0.3)
            print(f"Successfully wrote {name} as single file via webhdfs: {target_path}")
            print("Preview:")
            print(hdfs_head(target_path, n=20))
            return
        except Exception as e:
            print(f"Driver write failed for {name}: {e}")
            traceback.print_exc()
            print("Falling back to coalesce(1) + mv method...")

    # Fallback: write coalesce(1) into tmp dir and mv
    print(f"Fallback: writing {name} via Spark coalesce(1) into tmp dir {tmp_dir}")
    rc, out = hdfs_rmdir(tmp_dir)
    if rc != 0:
        print(f"hdfs_rmdir returned rc={rc}: {out}")
    try:
        df.coalesce(1).write.mode("overwrite").option("header", "true").csv(f"{HDFS_RPC}{tmp_dir}")
    except Exception as e:
        print(f"Spark write failed for {name}: {e}")
        traceback.print_exc()
        raise

    time.sleep(0.5)
    part_path, listing = find_part_file_in_tmp(tmp_dir)
    print(f"Listing of tmp dir ({tmp_dir}):\n{listing}")
    if not part_path:
        raise RuntimeError(f"Aucun part-*.csv trouvé dans {tmp_dir} après écriture.")
    print(f"Found part file: {part_path}. Moving to {target_path} ...")
    ok, msg = move_part_to_target(part_path, target_path, tmp_dir)
    if not ok:
        raise RuntimeError(f"Failed to move part file to target: {msg}")
    print(f"Successfully moved part -> {target_path} ({msg})")
    print("Preview:")
    print(hdfs_head(target_path, n=20))

    # Ajout: Enregistrement au format DuckDB localement et upload sur HDFS
    local_duckdb_path = f"/tmp/{name}.duckdb"
    duckdb_hdfs_path = f"/data_processed/{name}.duckdb"
    try:
        print(f"Saving {name} as DuckDB file: {local_duckdb_path}")
        save_df_to_duckdb(df, local_duckdb_path, table_name=name)
        print(f"Uploading DuckDB file to HDFS: {duckdb_hdfs_path}")
        client.upload(duckdb_hdfs_path, local_duckdb_path, overwrite=True)
        print(f"Done: {duckdb_hdfs_path} available in HDFS.")
    except Exception as e:
        print(f"Erreur DuckDB export/upload pour {name}: {e}")
    finally:
        try:
            os.remove(local_duckdb_path)
        except Exception:
            pass

def main():
    spark = SparkSession.builder.appName("NBACSVSingleFile_v4").getOrCreate()
    try:
        # CAREER (question 1) : lire, préparer et ajouter colonnes de variation
        print("Reading career dataset via Spark...")
        df_career = spark.read.csv(f"{HDFS_RPC}{career_input}", header=True, inferSchema=True)
        cols = [
            "PLAYER_ID","SEASON_ID","TEAM_ID","GP","MIN","FGM","FGA","FG_PCT",
            "FTM","FTA","FT_PCT","OREB","DREB","REB","AST","STL","BLK","TOV","PF","PTS"
        ]
        # select intersection afin d'être résilient si certaines colonnes manquent
        available = [c for c in cols if c in df_career.columns]
        df_career = df_career.dropDuplicates(["PLAYER_ID", "SEASON_ID"]).select(*available)

        # --- AJOUT: calcul des variations de performance saison -> saison-1
        # appliquer add_performance_variation_columns sur df_career
        df_career = add_performance_variation_columns(df_career, id_col="PLAYER_ID", season_col="SEASON_ID")

        process_and_write(df_career, "career_stats", career_target, career_tmp, spark)

        # SPECTACULAR GAMES
        print("Reading games dataset via Spark...")
        df_games = spark.read.csv(games_input_rpc, header=True, inferSchema=True)
        cols_to_keep = [
            "season_id","team_id_home","game_id","game_date","fgm_home","fga_home","fg_pct_home",
            "reb_home","ast_home","stl_home","blk_home","tov_home","pts_home",
            "fgm_away","fga_away","fg_pct_away","reb_away","ast_away","stl_away","blk_away","tov_away","pts_away","season_type"
        ]
        available_games = [c for c in cols_to_keep if c in df_games.columns]
        df_games = df_games.select(*available_games)

        def safe_sum(col_home, col_away, alias):
            if col_home in df_games.columns and col_away in df_games.columns:
                return (col(col_home) + col(col_away)).alias(alias)
            elif col_home in df_games.columns:
                return col(col_home).alias(alias)
            elif col_away in df_games.columns:
                return col(col_away).alias(alias)
            else:
                from pyspark.sql.functions import lit
                return lit(0).alias(alias)

        df_games = df_games.withColumn("pts", safe_sum("pts_home", "pts_away", "pts")) \
                           .withColumn("reb", safe_sum("reb_home", "reb_away", "reb")) \
                           .withColumn("ast", safe_sum("ast_home", "ast_away", "ast")) \
                           .withColumn("stl", safe_sum("stl_home", "stl_away", "stl")) \
                           .withColumn("blk", safe_sum("blk_home", "blk_away", "blk")) \
                           .withColumn("tov", safe_sum("tov_home", "tov_away", "tov"))

        final_cols = [c for c in ["season_id","game_id","game_date","season_type","pts","reb","ast","stl","blk","tov"] if c in df_games.columns]
        df_games = df_games.select(*final_cols)

        print("Top rows (sanity):")
        df_games.show(5, truncate=False)

        df_ranked = df_games.orderBy(col("pts").desc()).limit(10)
        process_and_write(df_ranked, "spectacular_games", spectacular_target, spectacular_tmp, spark)

        print("All done.")
    except Exception as e:
        print("Erreur lors du traitement principal :", e)
        traceback.print_exc()
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    main()