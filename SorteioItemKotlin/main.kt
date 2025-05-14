package com.example.sorteioitem

import android.os.Bundle
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import java.io.BufferedReader
import java.io.InputStreamReader
import kotlin.random.Random
import org.apache.commons.text.similarity.LevenshteinDistance

class MainActivity : AppCompatActivity() {

    private lateinit var btnFuzz: Button
    private lateinit var inputTexto: EditText
    private lateinit var resultadoTexto: TextView
    private lateinit var textoSorteado: TextView

    private var itemSorteado: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Inicializações após setContentView
        btnFuzz = findViewById(R.id.btnFuzz)
        inputTexto = findViewById(R.id.input_text)
        resultadoTexto = findViewById(R.id.fuzzShowing)
        textoSorteado = findViewById(R.id.data)

        val descricoes = mutableListOf<String>()

        // Lê o arquivo CSV
        assets.open("tabela_consulta2.csv").bufferedReader().useLines { lines ->
            lines.forEach { line ->
                val row = line.split(",")
                if (row.size >= 2) {
                    descricoes.add(row[0].replace("\"", "").trim())
                }
            }
        }

        // Sorteia um item
        if (descricoes.isNotEmpty()) {
            itemSorteado = descricoes[Random.nextInt(descricoes.size)]
            textoSorteado.text = itemSorteado
        } else {
            textoSorteado.text = "Nenhuma descrição encontrada."
        }

        // Define a ação do botão
        btnFuzz.setOnClickListener {
            val entrada = inputTexto.text.toString()
            val resultado = levenshteinSimilarity(entrada, itemSorteado) * 100
            resultadoTexto.text = "Similaridade: ${resultado.toInt()}%"
        }
    }

    // Função de similaridade
    private fun levenshteinSimilarity(a: String, b: String): Double {
        val distance = LevenshteinDistance().apply(a, b)
        val maxLen = maxOf(a.length, b.length)
        return if (maxLen == 0) 1.0 else 1.0 - (distance.toDouble() / maxLen)
    }
}
