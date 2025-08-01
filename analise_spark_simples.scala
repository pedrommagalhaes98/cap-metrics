// Análise rápida: % de retornos após chamadas "unanswered" por variant
// Assumindo que você já tem callsXpDf carregado como DataFrame

import org.apache.spark.sql.functions._
import org.apache.spark.sql.expressions.Window

// Window para ordenar por cliente e call_id
val window = Window.partitionBy("customer__id").orderBy("call__id")

// Adicionar interpretation da chamada anterior e filtrar retornos
val resultado = callsXpDf
  .withColumn("interpretation_anterior", lag("interpretation", 1).over(window))
  .filter($"first_contact_in_24_hours" === false)  // Só retornos
  .filter($"interpretation_anterior".isNotNull)    // Que têm chamada anterior
  .groupBy("variant")
  .agg(
    count("*").alias("total_retornos"),
    sum(when($"interpretation_anterior" === "unanswered", 1).otherwise(0)).alias("unanswered_anterior"),
    avg(when($"interpretation_anterior" === "unanswered", 1.0).otherwise(0.0)).alias("percentual")
  )
  .withColumn("percentual", round($"percentual" * 100, 2))
  .orderBy("variant")

println("% de retornos após chamadas 'unanswered' por variant:")
resultado.show()

// Se quiser salvar o resultado:
// resultado.write.mode("overwrite").csv("caminho/resultado_analise") 