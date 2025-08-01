import org.apache.spark.sql.{DataFrame, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window

object AnaliseRetornoChamadas {
  
  def analisarRetornoVsUnanswered(spark: SparkSession, callsXpDf: DataFrame): DataFrame = {
    import spark.implicits._
    
    // Window para ordenar chamadas por cliente e call_id
    val windowSpec = Window
      .partitionBy("customer__id")
      .orderBy("call__id")
    
    // Adicionar coluna com interpretation da chamada anterior
    val dfComAnterior = callsXpDf
      .withColumn("interpretation_anterior", lag("interpretation", 1).over(windowSpec))
      .withColumn("call__id_anterior", lag("call__id", 1).over(windowSpec))
    
    // Filtrar apenas chamadas de retorno que têm chamada anterior
    val retornos = dfComAnterior
      .filter($"first_contact_in_24_hours" === false)
      .filter($"interpretation_anterior".isNotNull)
    
    // Calcular se a chamada anterior foi unanswered
    val retornosComFlag = retornos
      .withColumn("foi_unanswered_anterior", 
        when($"interpretation_anterior" === "unanswered", true).otherwise(false))
    
    // Estatísticas por variant
    val estatisticasPorVariant = retornosComFlag
      .groupBy("variant")
      .agg(
        count("*").alias("total_retornos"),
        sum(when($"foi_unanswered_anterior", 1).otherwise(0)).alias("retornos_pos_unanswered"),
        avg(when($"foi_unanswered_anterior", 1.0).otherwise(0.0)).alias("percentual")
      )
      .withColumn("percentual", round($"percentual" * 100, 2))
      .orderBy("variant")
    
    // Mostrar resultados
    println("=== ANÁLISE: % DE RETORNOS APÓS CHAMADAS 'UNANSWERED' POR VARIANT ===")
    estatisticasPorVariant.show()
    
    // Estatísticas gerais
    val estatisticasGerais = retornosComFlag
      .agg(
        count("*").alias("total_retornos"),
        sum(when($"foi_unanswered_anterior", 1).otherwise(0)).alias("retornos_pos_unanswered")
      )
      .withColumn("percentual_geral", 
        round($"retornos_pos_unanswered" / $"total_retornos" * 100, 2))
    
    println("\n=== ESTATÍSTICAS GERAIS ===")
    estatisticasGerais.show()
    
    // Distribuição dos status anteriores
    val distribuicaoStatus = retornosComFlag
      .groupBy("interpretation_anterior")
      .agg(count("*").alias("quantidade"))
      .withColumn("percentual", 
        round($"quantidade" / sum("quantidade").over() * 100, 2))
      .orderBy(desc("quantidade"))
    
    println("\n=== DISTRIBUIÇÃO DOS STATUS ANTERIORES ===")
    distribuicaoStatus.show()
    
    estatisticasPorVariant
  }
  
  // Versão mais detalhada que retorna o dataset com as flags
  def analisarRetornoDetalhado(spark: SparkSession, callsXpDf: DataFrame): DataFrame = {
    import spark.implicits._
    
    val windowSpec = Window
      .partitionBy("customer__id")
      .orderBy("call__id")
    
    val resultado = callsXpDf
      .withColumn("interpretation_anterior", lag("interpretation", 1).over(windowSpec))
      .withColumn("call__id_anterior", lag("call__id", 1).over(windowSpec))
      .withColumn("foi_retorno", $"first_contact_in_24_hours" === false)
      .withColumn("foi_unanswered_anterior", 
        when($"interpretation_anterior" === "unanswered", true).otherwise(false))
      .withColumn("retorno_pos_unanswered", 
        $"foi_retorno" && $"foi_unanswered_anterior")
    
    resultado
  }
  
  // Função de uso rápido
  def analiseRapida(spark: SparkSession, callsXpDf: DataFrame): Unit = {
    import spark.implicits._
    
    val resultado = callsXpDf
      .withColumn("interpretation_anterior", 
        lag("interpretation", 1).over(
          Window.partitionBy("customer__id").orderBy("call__id")
        ))
      .filter($"first_contact_in_24_hours" === false)
      .filter($"interpretation_anterior".isNotNull)
      .groupBy("variant")
      .agg(
        count("*").alias("total_retornos"),
        avg(when($"interpretation_anterior" === "unanswered", 1.0).otherwise(0.0)).alias("perc_unanswered")
      )
      .withColumn("perc_unanswered", round($"perc_unanswered" * 100, 2))
      .orderBy("variant")
    
    println("% de retornos após chamadas 'unanswered' por variant:")
    resultado.show()
  }
}

// Exemplo de uso:
/*
val spark = SparkSession.builder()
  .appName("Análise Retorno Chamadas")
  .getOrCreate()

// Assumindo que callsXpDf já está carregado
val resultado = AnaliseRetornoChamadas.analisarRetornoVsUnanswered(spark, callsXpDf)

// Para análise rápida:
AnaliseRetornoChamadas.analiseRapida(spark, callsXpDf)

// Para dataset detalhado:
val detalhado = AnaliseRetornoChamadas.analisarRetornoDetalhado(spark, callsXpDf)
detalhado.write.mode("overwrite").parquet("caminho/para/salvar/analise_detalhada")
*/ 