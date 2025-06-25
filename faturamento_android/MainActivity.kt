package com.example.faturamento1

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import kotlin.random.Random
import org.apache.commons.text.similarity.LevenshteinDistance

class MainActivity : AppCompatActivity() {

    private lateinit var speechRecognizer: SpeechRecognizer
    private lateinit var btnFuzz: Button
    private lateinit var btnFalar: Button
    private lateinit var btnNovoTermo: Button
    private lateinit var inputTexto: TextView  // Agora é TextView
    private lateinit var resultadoTexto: TextView
    private lateinit var textoSorteado: TextView

    private var itemSorteado: String = ""

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Inicializações
        btnFuzz = findViewById(R.id.btnFuzz)
        btnFalar = findViewById(R.id.btnGrava)
        inputTexto = findViewById(R.id.input_text)
        resultadoTexto = findViewById(R.id.fuzzShowing)
        textoSorteado = findViewById(R.id.data)
        btnNovoTermo = findViewById((R.id.btnAlterna))

        solicitarPermissoes()

        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
        configurarReconhecimento()

        val descricoes = mutableListOf<String>()

        // Lê o arquivo CSV
        assets.open("tabela_consulta3.csv").bufferedReader().useLines { lines ->
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

        // Ação do botão de similaridade
        btnFuzz.setOnClickListener {
            val entrada = inputTexto.text.toString()
            val resultado = levenshteinSimilarity(entrada, itemSorteado) * 100
            resultadoTexto.text = "Similaridade: ${resultado.toInt()}%"
            if(resultado.toInt() > 90){
                itemSorteado = descricoes[Random.nextInt(descricoes.size)]
                textoSorteado.text = itemSorteado
            }
        }

        btnFalar.setOnClickListener {
            iniciarReconhecimentoVoz()
        }


        btnNovoTermo.setOnClickListener {
            itemSorteado = descricoes[Random.nextInt(descricoes.size)]
            textoSorteado.text = itemSorteado
        }
    }

    private fun solicitarPermissoes() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED
        ) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 1)
        }
    }

    private fun configurarReconhecimento() {
        speechRecognizer.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {}
            override fun onBeginningOfSpeech() {}
            override fun onRmsChanged(rmsdB: Float) {}
            override fun onBufferReceived(buffer: ByteArray?) {}
            override fun onEndOfSpeech() {}

            override fun onResults(results: Bundle?) {
                val palavras = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!palavras.isNullOrEmpty()) {
                    val textoCapturado = palavras.joinToString(" ").uppercase()
                    inputTexto.text = textoCapturado
                }
            }

            override fun onError(error: Int) {}
            override fun onPartialResults(partialResults: Bundle?) {}
            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
    }

    private fun iniciarReconhecimentoVoz() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, "pt-BR")
        }
        speechRecognizer.startListening(intent)
    }

    private fun levenshteinSimilarity(a: String, b: String): Double {
        val distance = LevenshteinDistance().apply(a, b)
        val maxLen = maxOf(a.length, b.length)
        return if (maxLen == 0) 1.0 else 1.0 - (distance.toDouble() / maxLen)
    }

    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer.destroy()
    }
}
