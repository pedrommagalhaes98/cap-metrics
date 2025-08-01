import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window

object AnaliseCompletaDia {
  
  def analisarRetornoVsUnansweredPorDia(spark: SparkSession, callsXpDf: DataFrame): DataFrame = {
    import spark.implicits._
    
    // Window para ordenar chamadas por cliente e call_id
    val windowSpec = Window
      .partitionBy("customer__id")
      .orderBy("call__id")
    
    // Transformar start_at em data e adicionar interpretation anterior
    val dfComData = callsXpDf
      .withColumn("data_chamada", to_date($"start_at"))
      .withColumn("interpretation_anterior", lag("interpretation", 1).over(windowSpec))
      .withColumn("call__id_anterior", lag("call__id", 1).over(windowSpec))
    
    // Filtrar apenas chamadas de retorno que têm chamada anterior
    val retornos = dfComData
      .filter($"first_contact_in_24_hours" === false)
      .filter($"interpretation_anterior".isNotNull)
    
    // Calcular se a chamada anterior foi unanswered
    val retornosComFlag = retornos
      .withColumn("foi_unanswered_anterior", 
        when($"interpretation_anterior" === "unanswered", true).otherwise(false))
    
    // Window para calcular diferenças por data
    val windowPorData = Window.partitionBy("data_chamada")
    
    // Estatísticas por dia e variant com diferença treatment-b vs control
    val estatisticasPorDiaVariant = retornosComFlag
      .groupBy("data_chamada", "variant")
      .agg(
        count("*").alias("total_retornos"),
        sum(when($"foi_unanswered_anterior", 1).otherwise(0)).alias("retornos_pos_unanswered"),
        avg(when($"foi_unanswered_anterior", 1.0).otherwise(0.0)).alias("percentual")
      )
      .withColumn("percentual", round($"percentual" * 100, 2))
      .withColumn("control_perc", 
        when($"variant" === "control", $"percentual")
        .otherwise(max(when($"variant" === "control", $"percentual")).over(windowPorData)))
      .withColumn("treatment_b_perc", 
        when($"variant" === "treatment-b", $"percentual")
        .otherwise(max(when($"variant" === "treatment-b", $"percentual")).over(windowPorData)))
      .withColumn("diff_treatment_b_vs_control", 
        coalesce($"treatment_b_perc", lit(0.0)) - coalesce($"control_perc", lit(0.0)))
      .orderBy("data_chamada", "variant")
    
    // Mostrar resultados
    println("=== ANÁLISE: % DE RETORNOS APÓS 'UNANSWERED' POR DIA E VARIANT ===")
    estatisticasPorDiaVariant.show(100, false)
    
    // Estatísticas apenas por dia (agregado de todos variants)
    val estatisticasPorDia = retornosComFlag
      .groupBy("data_chamada")
      .agg(
        count("*").alias("total_retornos"),
        sum(when($"foi_unanswered_anterior", 1).otherwise(0)).alias("retornos_pos_unanswered"),
        avg(when($"foi_unanswered_anterior", 1.0).otherwise(0.0)).alias("percentual")
      )
      .withColumn("percentual", round($"percentual" * 100, 2))
      .orderBy("data_chamada")
    
    println("\n=== EVOLUÇÃO DIÁRIA (TODOS OS VARIANTS) ===")
    estatisticasPorDia.show(100, false)
    
    // Estatísticas apenas por variant (agregado de todos os dias)
    val estatisticasPorVariant = retornosComFlag
      .groupBy("variant")
      .agg(
        count("*").alias("total_retornos"),
        sum(when($"foi_unanswered_anterior", 1).otherwise(0)).alias("retornos_pos_unanswered"),
        avg(when($"foi_unanswered_anterior", 1.0).otherwise(0.0)).alias("percentual")
      )
      .withColumn("percentual", round($"percentual" * 100, 2))
      .orderBy("variant")
    
    println("\n=== RESUMO POR VARIANT (TODOS OS DIAS) ===")
    estatisticasPorVariant.show()
    
    estatisticasPorDiaVariant
  }
} 