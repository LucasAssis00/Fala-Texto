package com.example.transcrevetudo


import android.Manifest
import android.app.AlertDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Bundle
import android.os.Environment
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.widget.Button
import android.widget.CheckBox
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.RadioButton
import android.widget.RadioGroup
import android.widget.TextView
import android.widget.Toast
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContentProviderCompat.requireContext
import androidx.core.content.ContextCompat
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import java.io.File
import java.io.FileOutputStream
import java.io.OutputStreamWriter
import java.io.PrintWriter


sealed class Question(val title: String)
class MultipleChoiceQuestion(title: String, val options: List<String>) : Question(title)
class TextInputQuestion(title: String) : Question(title)
class CheckboxQuestion(
    title: String,
    val options: List<String>
) : Question(title)



class MainActivity : AppCompatActivity() {

    private lateinit var container: FrameLayout
    private lateinit var btnNext: Button
    private lateinit var btnFalar: Button
    private lateinit var btnToast: Button

    private lateinit var speechRecognizer: SpeechRecognizer
    private lateinit var currentQuestionView: View

    private lateinit var textView: TextView



    private val questions: List<Question> = listOf(

        TextInputQuestion("Nome:"),
        TextInputQuestion("Prontuário:"),
        TextInputQuestion("Sala:"),
        CheckboxQuestion("Paciente confirmou:", listOf("Identidade", "Sítio Cirúrgico correto", "Procedimento", "Consentimento")),
        MultipleChoiceQuestion("Sítio demarcado (lateralidade):", listOf("Sim", "Não", "Não se aplica")),
        CheckboxQuestion("Verificação da segurança anestésica:", listOf("Montagem da SO de acordo com o procedimento", "Material anestésico disponível, revisados e funcionantes")),
        TextInputQuestion("Verificação da segurança anestésica (Outro):"),
        MultipleChoiceQuestion("Via aérea difícil/broncoaspiração:", listOf("Não", "Sim e equipamento/assistência disponíveis")),
        CheckboxQuestion("Risco de grande perda sanguínea superior a 500 ml ou mais 7 ml/kg em crianças:", listOf("Sim", "Não", "Reserva de sangue disponível")),
        CheckboxQuestion("Acesso venoso adequado e pérvio:", listOf("Sim", "Não", "Providenciado na SO")),
        MultipleChoiceQuestion("Histórico de reação alérgica:", listOf("Sim", "Não")),
        TextInputQuestion("Qual?:"),

        TextInputQuestion("Responsável:"),
        TextInputQuestion("Data:"),
    )

    private var currentIndex = 0
    private val answers = mutableMapOf<Int, String>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        textView = findViewById(R.id.textView)
        container = findViewById(R.id.question_container)
        btnNext = findViewById(R.id.btn_next)
        btnFalar = findViewById(R.id.btnFalar)
        //btnToast = findViewById(R.id.btn_toast)

        showCurrentQuestion()

        btnNext.setOnClickListener {
            saveCurrentAnswer()

            if (currentIndex < questions.size - 1) {
                currentIndex++
                showCurrentQuestion()
            } else {
                val alert = AlertDialog.Builder(this)
                    .setTitle("Fim das perguntas")
                    .setMessage("Você completou todas as perguntas!")
                    .setPositiveButton("Recomeçar") { _, _ ->
                        salvarRespostasEmCSV()
                        currentIndex = 0
                        answers.clear() // se quiser limpar as respostas, opcional
                        showCurrentQuestion()
                    }
                    .setNegativeButton("Cancelar", null)
                    .create()

                alert.show()
            }
        }
        solicitarPermissoes()

        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
        configurarReconhecimento()

        btnFalar.setOnClickListener {
            iniciarReconhecimentoVoz()
        }

    }

    private fun showCurrentQuestion() {
        //fun showCurrentQuestion() {
        val inflater = LayoutInflater.from(this)
        val question = questions[currentIndex]

        val layoutId = when (question) {
            is TextInputQuestion -> R.layout.question_text_input
            is MultipleChoiceQuestion -> R.layout.question_multiple_choice
            is CheckboxQuestion -> R.layout.question_checkbox // <- este aqui!
            else -> throw IllegalArgumentException("Tipo desconhecido de pergunta")
        }


        val view = inflater.inflate(layoutId, container, false)
        container.removeAllViews()
        container.addView(view)

        currentQuestionView = view

        //val subtitle = view.findViewById<TextView?>(R.id.question_header)
        // Preencher o conteúdo
        val title = view.findViewById<TextView>(R.id.question_title)

        //subtitle?.text = "Pergunta ${currentIndex + 1} de ${questions.size}"
        title.text = question.title

        if (question is MultipleChoiceQuestion) {
            val group = view.findViewById<RadioGroup>(R.id.options_group)
            group.removeAllViews()
            for (option in question.options) {
                val rb = RadioButton(this)
                rb.text = option
                group.addView(rb)
            }
        }
        if (question is CheckboxQuestion) {
            val title = view.findViewById<TextView>(R.id.question_title)
            title.text = question.title

            val container = view.findViewById<LinearLayout>(R.id.checkbox_container)
            container.removeAllViews()

            for (option in question.options) {
                val cb = CheckBox(this) // ou `requireContext()` no Fragment
                cb.text = option
                container.addView(cb)
            }
        }
        currentQuestionView = view // <- guarde a referência
    }
    private fun saveCurrentAnswer() {
        val question = questions[currentIndex]
        val view = container.getChildAt(0) ?: return

        val response: String = when (question) {
            is MultipleChoiceQuestion -> {
                val group = view.findViewById<RadioGroup>(R.id.options_group)
                val selectedId = group.checkedRadioButtonId
                if (selectedId != -1) {
                    val radioButton = view.findViewById<RadioButton>(selectedId)
                    radioButton.text.toString()
                } else {
                    ""
                }
            }
            is TextInputQuestion -> {
                val input = view.findViewById<EditText>(R.id.input_answer)
                input.text.toString()
            }
            is CheckboxQuestion -> {
                val checkboxContainer = view.findViewById<LinearLayout>(R.id.checkbox_container)
                val selected = mutableListOf<String>()
                for (i in 0 until checkboxContainer.childCount) {
                    val checkBox = checkboxContainer.getChildAt(i) as? CheckBox
                    if (checkBox?.isChecked == true) {
                        selected.add(checkBox.text.toString())
                    }
                }
                selected.joinToString("; ") // <-- isso vira a resposta
            }
        }

        answers[currentIndex] = response
    }
    private fun salvarRespostasEmCSV() {
        val directory = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
        var fileNumber = 1
        var file: File
        do {
            val fileName = "respostas$fileNumber.csv"
            file = File(directory, fileName)
            fileNumber++
        } while (file.exists()) // Continua até encontrar um nome de arquivo que não existe



        try {
            val fileOutputStream = FileOutputStream(file)

            val writer = PrintWriter(OutputStreamWriter(fileOutputStream, "UTF-8"))

            writer.println("Pergunta,Resposta")
            for ((index, question) in questions.withIndex()) {
                val pergunta = question.title
                val resposta = answers[index] ?: ""
                writer.println("\"$pergunta\",\"$resposta\"")
            }

            writer.flush()
            writer.close()

            Toast.makeText(this, "Salvo em: ${file.absolutePath}", Toast.LENGTH_LONG).show()
        } catch (e: Exception) {
            Toast.makeText(this, "Erro ao salvar: ${e.message}", Toast.LENGTH_LONG).show()
            e.printStackTrace()
        }
    }
    private fun solicitarPermissoes() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.RECORD_AUDIO), 1)
        }
    }
    private fun configurarReconhecimento() {
        speechRecognizer.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                textView.text = "Fale agora..."
            }

            override fun onBeginningOfSpeech() {
                textView.text = "Ouvindo..."
            }

            private fun marcarCheckboxComTexto(texto: String) {
                val container = currentQuestionView.findViewById<LinearLayout>(R.id.checkbox_container)
                for (i in 0 until container.childCount) {
                    val cb = container.getChildAt(i) as? CheckBox
                    if (cb != null && cb.text.toString().equals(texto, ignoreCase = true)) {
                        cb.isChecked = true
                    }
                }
            }

            private fun marcarRadioButtonComTexto(texto: String) {
                val group = currentQuestionView.findViewById<RadioGroup>(R.id.options_group)
                for (i in 0 until group.childCount) {
                    val rb = group.getChildAt(i) as? RadioButton
                    if (rb != null && rb.text.toString().equals(texto, ignoreCase = true)) {
                        rb.isChecked = true
                        break
                    }
                }
            }

            override fun onRmsChanged(rmsdB: Float) {}

            override fun onBufferReceived(buffer: ByteArray?) {}

            override fun onEndOfSpeech() {
                textView.text = "Processando..."
            }

            private fun verificarEExecutar(
                gatilho: String,
                textoCapturado: String,
                confirmacao: String,
                respostas: List<String> = listOf("não", "sim")
            ) {
                if (confirmacao.trim().startsWith(gatilho, ignoreCase = true)) {
                    respostas.forEach { resposta ->
                        if (textoCapturado.contains(resposta, ignoreCase = true)) {
                            marcarRadioButtonComTexto(resposta.replaceFirstChar { it.uppercaseChar() })
                            return // para evitar múltiplos disparos
                        }
                    }
                }
            }


            override fun onResults(results: Bundle?) {
                val input = currentQuestionView.findViewById<EditText>(R.id.input_answer)

                val confirmacao = currentQuestionView.findViewById<TextView>(R.id.question_title).text.toString()

                val palavras = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                if (!palavras.isNullOrEmpty()) {
                    val textoCapturado = palavras.joinToString(" ")
                    textView.text = "Você disse: $textoCapturado"

                    if (confirmacao.trim().startsWith("Nome", ignoreCase = true) && textoCapturado.contains("nome", ignoreCase = true)) {
                        val output_string = textoCapturado.substringAfter("nome ").trim()
                        input.setText(output_string)
                    }
                    if (confirmacao.trim().startsWith("Prontuário", ignoreCase = true)) {
                        val output_string = textoCapturado.substringAfter("prontuário ").trim()
                        input.setText(output_string)
                    }
                    if (confirmacao.trim().startsWith("Sala", ignoreCase = true)) {
                        val output_string = textoCapturado.substringAfter("sala ").trim()
                        input.setText(output_string)
                    }
                    if (confirmacao.trim().startsWith("Paciente confirmou", ignoreCase = true)) {
                        if (textoCapturado.contains("identidade", ignoreCase = true)) {
                            marcarCheckboxComTexto("Identidade")
                        }
                        if (textoCapturado.contains("sítio cirúrgico", ignoreCase = true)) {
                            marcarCheckboxComTexto("Sítio Cirúrgico correto")
                        }
                        if (textoCapturado.contains("procedimento", ignoreCase = true)) {
                            marcarCheckboxComTexto("Procedimento")
                        }
                        if (textoCapturado.contains("consentimento", ignoreCase = true)) {
                            marcarCheckboxComTexto("Consentimento")
                        }
                    }
                    //verificarEExecutar("sítio demarcado", textoCapturado, confirmacao)

                    if (confirmacao.trim().startsWith("sítio demarcado", ignoreCase = true)) {
                        if (textoCapturado.contains("não se aplica", ignoreCase = true)) {
                            marcarRadioButtonComTexto("não se aplica")
                        } else if (textoCapturado.contains("não", ignoreCase = true)) {
                            marcarRadioButtonComTexto("não")
                        } else if (textoCapturado.contains("sim", ignoreCase = true)) {
                            marcarRadioButtonComTexto("Sim")
                        }
                    }

                    if (confirmacao.trim().endsWith("segurança anestésica:", ignoreCase = true)) {
                        if (textoCapturado.contains("montagem da so", ignoreCase = true) or textoCapturado.contains("de acordo com o procedimento", ignoreCase = true)) {
                            marcarCheckboxComTexto("Montagem da SO de acordo com o procedimento")
                        }
                        if (textoCapturado.contains("Material anestésico disponível", ignoreCase = true)) {
                            marcarCheckboxComTexto("Material anestésico disponível, revisados e funcionantes")
                        }
                    }
                    if (confirmacao.trim().endsWith("(Outro):", ignoreCase = true)) {
                        input.setText(textoCapturado)
                    }
                    if (confirmacao.trim().startsWith("Via aérea difícil", ignoreCase = true)) {
                        if (textoCapturado.contains("não", ignoreCase = true) ) {
                            marcarRadioButtonComTexto("Não")
                        } else if (textoCapturado.contains("sim", ignoreCase = true) ) {
                            marcarRadioButtonComTexto("Sim e equipamento/assistência disponíveis")
                        }
                    }
                    if (confirmacao.trim().startsWith("Risco de grande perda", ignoreCase = true)) {
                        if (textoCapturado.contains("não", ignoreCase = true) ) {
                            marcarCheckboxComTexto("Não")
                        } else if (textoCapturado.contains("sim", ignoreCase = true) ) {
                            marcarCheckboxComTexto("Sim")
                        }
                        if (textoCapturado.contains("reserva de sangue disponível", ignoreCase = true) ) {
                            marcarCheckboxComTexto("Reserva de sangue Disponível")
                        }
                    }
                    if (confirmacao.trim().startsWith("Acesso venoso", ignoreCase = true)) {
                        if (textoCapturado.contains("não", ignoreCase = true) ) {
                            marcarCheckboxComTexto("Não")
                        } else if (textoCapturado.contains("sim", ignoreCase = true) ) {
                            marcarCheckboxComTexto("Sim")
                        }
                        if (textoCapturado.contains("providenciado na", ignoreCase = true) ) {
                            marcarCheckboxComTexto("Providenciado na SO")
                        }
                    }
                    //verificarEExecutar("Histórico de reação", textoCapturado, confirmacao)
                    if (confirmacao.trim().startsWith("Histórico de reação", ignoreCase = true)) {
                        if (textoCapturado.contains("não", ignoreCase = true)) {
                            marcarRadioButtonComTexto("não")
                        } else if (textoCapturado.contains("sim", ignoreCase = true) ) {
                            marcarRadioButtonComTexto("Sim")
                        }
                    }

                    if (confirmacao.trim().endsWith("Qual?:", ignoreCase = true)) {
                        //val output_string = textoParcial.substringAfter("sala ").trim()
                        //input.setText(output_string)
                        input.setText(textoCapturado)
                    }
                    if (confirmacao.trim().startsWith("Responsável:", ignoreCase = true)) {
                        val output_string = textoCapturado.substringAfter("responsável ").trim()
                        input.setText(output_string)
                    }
                    if (confirmacao.trim().startsWith("Data:", ignoreCase = true)) {
                        val output_string = textoCapturado.substringAfter("data ").trim()
                        input.setText(output_string)
                    }
                    if (confirmacao.trim().startsWith("Data:", ignoreCase = true)) {
                        val output_string = textoCapturado.substringAfter("data ").trim()
                        input.setText(output_string)
                    }


                    if (textoCapturado.contains("próxima pergunta", ignoreCase = true)){
                        btnNext.performClick()
                    }
                } else {
                    textView.text = "Nenhum texto reconhecido"
                }

                //iniciarReconhecimentoVoz()
            }

            override fun onError(error: Int) {
                val mensagemErro = when (error) {
                    SpeechRecognizer.ERROR_AUDIO -> "Erro de áudio"
                    SpeechRecognizer.ERROR_CLIENT -> "Erro do cliente (reinicie o app)"
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "Permissão insuficiente"
                    SpeechRecognizer.ERROR_NETWORK -> "Erro de rede"
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "Tempo limite de rede"
                    SpeechRecognizer.ERROR_NO_MATCH -> "Nenhuma fala reconhecida"
                    SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "Reconhecedor ocupado"
                    SpeechRecognizer.ERROR_SERVER -> "Erro no servidor"
                    SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "Nenhum som detectado"
                    else -> "Erro desconhecido: $error"
                }
                //textView.text = mensagemErro
                //iniciarReconhecimentoVoz()
            }

            override fun onPartialResults(partialResults: Bundle?) {

            }

            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
    }
    private fun iniciarReconhecimentoVoz() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, "pt-BR")
            speechRecognizer.startListening(intent)
        }
        speechRecognizer.startListening(intent)
    }
    private fun processarTextoReconhecido(texto: String) {
        val question = questions[currentIndex]
        val view = currentQuestionView ?: return

        when (question) {
            is TextInputQuestion -> {
                val input = view.findViewById<EditText>(R.id.input_answer)
                input.setText(texto)
            }
            is MultipleChoiceQuestion -> {
                val group = view.findViewById<RadioGroup>(R.id.options_group)
                for (i in 0 until group.childCount) {
                    val rb = group.getChildAt(i) as? RadioButton
                    if (rb != null && texto.contains(rb.text.toString(), ignoreCase = true)) {
                        rb.isChecked = true
                        break
                    }
                }
            }
            is CheckboxQuestion -> {
                val container = view.findViewById<LinearLayout>(R.id.checkbox_container)
                for (i in 0 until container.childCount) {
                    val cb = container.getChildAt(i) as? CheckBox
                    if (cb != null && texto.contains(cb.text.toString(), ignoreCase = true)) {
                        cb.isChecked = true
                    }
                }
            }
        }
    }
}
