// Análise: % de retornos após chamadas unanswered por DIA e VARIANT
// Para usar: AnaliseRapidaPorDia.executar(spark, callsXpDf)

import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window

object AnaliseRapidaPorDia {
  def executar(spark: SparkSession, callsXpDf: DataFrame): Unit = {
    import spark.implicits._
    
    // Window para ordenar por cliente e call_id
    val window = Window.partitionBy("customer__id").orderBy("call__id")

    // Análise por dia e variant
    val estatisticasBase = callsXpDf
      .withColumn("data_chamada", to_date(col("start_at")))
      .withColumn("interpretation_anterior", lag("interpretation", 1).over(window))
      .filter(col("first_contact_in_24_hours") === false)
      .filter(col("interpretation_anterior").isNotNull)
      .groupBy("data_chamada", "variant")
      .agg(
        count("*").alias("total_retornos"),
        sum(when(col("interpretation_anterior") === "unanswered", 1).otherwise(0)).alias("unanswered_anterior"),
        avg(when(col("interpretation_anterior") === "unanswered", 1.0).otherwise(0.0)).alias("percentual")
      )
      .withColumn("percentual", round(col("percentual") * 100, 2))

    // Window para calcular diferenças por data
    val windowPorData = Window.partitionBy("data_chamada")

    // Adicionar coluna com diferença treatment-b vs control
    val resultadoPorDiaVariant = estatisticasBase
      .withColumn("control_perc", 
        when(col("variant") === "control", col("percentual"))
        .otherwise(max(when(col("variant") === "control", col("percentual"))).over(windowPorData)))
      .withColumn("treatment_b_perc", 
        when(col("variant") === "treatment-b", col("percentual"))
        .otherwise(max(when(col("variant") === "treatment-b", col("percentual"))).over(windowPorData)))
      .withColumn("diff_treatment_b_vs_control", 
        coalesce(col("treatment_b_perc"), lit(0.0)) - coalesce(col("control_perc"), lit(0.0)))
      .orderBy("data_chamada", "variant")

    println("% de retornos após chamadas unanswered por DIA e VARIANT:")
    resultadoPorDiaVariant.show(100, false)

    // Evolução apenas por dia (agregando todos os variants)
    val resultadoPorDia = callsXpDf
      .withColumn("data_chamada", to_date(col("start_at")))
      .withColumn("interpretation_anterior", lag("interpretation", 1).over(window))
      .filter(col("first_contact_in_24_hours") === false)
      .filter(col("interpretation_anterior").isNotNull)
      .groupBy("data_chamada")
      .agg(
        count("*").alias("total_retornos"),
        avg(when(col("interpretation_anterior") === "unanswered", 1.0).otherwise(0.0)).alias("percentual")
      )
      .withColumn("percentual", round(col("percentual") * 100, 2))
      .orderBy("data_chamada")

    println("\nEvolução diária (todos os variants):")
    resultadoPorDia.show(100, false)
  }
} 