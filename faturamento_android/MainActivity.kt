package com.example.faturamento1

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.widget.Button
import android.widget.PopupMenu
import android.widget.TextView
import android.widget.Toast
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
    private lateinit var btnRelatorio: Button
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
        btnRelatorio = findViewById(R.id.btnrelatorio)

        //mostrar a variavel como 'global'
        var tabela_final = mutableMapOf<String, String>()
        //var results: List<Pair<String, Int>> = emptyList()
        var results: List<Pair<Pair<String, String>, Int>> = emptyList()

        solicitarPermissoes()

        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
        configurarReconhecimento()

        val descricoes = mutableListOf<Pair<String, String>>()

        // Lê o arquivo CSV
        assets.open("tabela_consulta2.csv").bufferedReader().useLines { lines ->
            lines.drop(1).forEach { line -> // .drop(1) para ignorar o cabeçalho "Descricao,Valor"
                val row = line.split(",(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)".toRegex()) // regex que respeita aspas
                if (row.size >= 2) {
                    val descricao = row[0].replace("\"", "").trim()
                    val valor = row[1].replace("\"", "").trim()
                    descricoes.add(descricao to valor)
                }
            }
        }

        // Sorteia um item
        if (descricoes.isNotEmpty()) {
            val item = descricoes[Random.nextInt(descricoes.size)]
            itemSorteado = item.first
            //itemSorteado = descricoes[Random.nextInt(descricoes.size)]
            textoSorteado.text = itemSorteado
        } else {
            textoSorteado.text = "Nenhuma descrição encontrada."
        }

        // Ação do botão de similaridade
        btnFuzz.setOnClickListener {

            val entrada = inputTexto.text.toString()
            if (entrada.isBlank()) {
                textoSorteado.text = "Digite algo para comparar"
            }
            else {
                results = descricoes.map { it to (levenshteinSimilarity(entrada, it.first) * 100).toInt() }
                    .sortedByDescending { it.second }
                    .take(3) // top 3 mais parecidos

                val resultText = results.joinToString("\n\n") { (item, score) -> "${item.first}: $score%" }

                //textoSorteado.text = "Mais semelhantes:\n$resultText"
                resultadoTexto.text = "Mais semelhantes:\n$resultText"
                //resultadoTexto.text = "Mais semelhantes:\n${results[1].first}"
            }
            /*
            val resultado = levenshteinSimilarity(entrada, itemSorteado) * 100
            resultadoTexto.text = "Similaridade: ${resultado.toInt()}%"
            if(resultado.toInt() > 90){
                itemSorteado = descricoes[Random.nextInt(descricoes.size)]
                textoSorteado.text = itemSorteado
            }
             */
        }

        btnFalar.setOnClickListener {
            iniciarReconhecimentoVoz()
        }
        btnRelatorio.setOnClickListener {
            resultadoTexto.text = "Formulário:\n" + tabela_final.entries.joinToString("\n" ){ "*${it.key} - R$${it.value}" }
            //resultadoTexto.text = "Formulário:\n$tabela_final"
            //resultadoTexto.text = "Mais semelhantes:\n$resultText"
        }


        btnNovoTermo.setOnClickListener { view ->
            val popupMenu = PopupMenu(this@MainActivity, view)
            popupMenu.inflate(R.menu.popup_menu_item)

            fun processarSelecao(index: Int) {
                if (index in results.indices) {
                    val selecionado = results[index]
                    val descricao = selecionado.first.first
                    val valor = selecionado.first.second
                    val score = selecionado.second

                    Toast.makeText(this@MainActivity, selecionado.first.toString(), Toast.LENGTH_LONG).show()
                    //tabela_final.put(descricao, score.toString())
                    tabela_final.put(descricao, valor)
                    val novoItem = descricoes.random()
                    itemSorteado = novoItem.first
                    textoSorteado.text = "${novoItem.first}"
                    //textoSorteado.text = "${novoItem.first} - R$ ${novoItem.second}"
                    inputTexto.setText("Fala reconhecida aparecerá aqui")
                    resultadoTexto.text = ""
                    //textoSorteado.text = itemSorteado
                    //inputTexto.text = "Fala reconhecida aparecerá aqui"
                    //resultadoTexto.text = ""
                }
            }

            popupMenu.setOnMenuItemClickListener { menuItem ->
                when(menuItem.itemId){
                    R.id.item1 ->{
                        processarSelecao(0)
                        true
                    }

                    R.id.item2 ->{
                        processarSelecao(1)
                        true
                    }

                    R.id.item3 ->{
                        processarSelecao(2)
                        true
                    }

                    else ->{
                        false
                    }
                }
            }
            popupMenu.show()
        }
        /*
        btnNovoTermo.setOnClickListener {
            itemSorteado = descricoes[Random.nextInt(descricoes.size)]
            textoSorteado.text = ""
            //textoSorteado.text = itemSorteado
        }
        */
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
